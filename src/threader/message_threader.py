from typing import Dict, List, Optional
from datetime import datetime
import re
from collections import defaultdict

class MessageThreader:
    """Organizes parsed OFW messages into conversation threads"""
    
    def __init__(self):
        self.threads = defaultdict(list)
        self.thread_metadata = {}
        
    def thread_messages(self, messages: List[Dict]) -> Dict:
        """
        Takes parsed messages and organizes them into conversation threads.
        Returns thread structure with metadata.
        """
        # Sort messages by timestamp
        sorted_msgs = sorted(messages, key=lambda x: x['timestamp'] if x['timestamp'] else '0')
        
        # First pass: Identify thread roots and build initial threads
        for msg in sorted_msgs:
            thread_id = self._identify_thread(msg)
            self.threads[thread_id].append(msg)
            
            # Update thread metadata
            if thread_id not in self.thread_metadata:
                self.thread_metadata[thread_id] = {
                    'subject': msg.get('subject'),
                    'start_time': msg['timestamp'],
                    'participants': set([msg['from'], msg['to']]),
                    'message_count': 1,
                    'last_message_time': msg['timestamp']
                }
            else:
                metadata = self.thread_metadata[thread_id]
                metadata['participants'].add(msg['from'])
                metadata['participants'].add(msg['to'])
                metadata['message_count'] += 1
                if msg['timestamp'] > metadata['last_message_time']:
                    metadata['last_message_time'] = msg['timestamp']
        
        # Second pass: Build parent-child relationships
        for thread_id, thread_messages in self.threads.items():
            self._build_message_relationships(thread_messages)
        
        # Prepare output
        return self._prepare_output()
    
    def _identify_thread(self, message: Dict) -> str:
        """
        Identifies which thread a message belongs to based on subject and content.
        Returns thread identifier.
        """
        # Clean subject line
        subject = message.get('subject', '').lower()
        subject = re.sub(r'^re:\s*', '', subject)
        
        # Look for references to previous messages
        content = message.get('content', '')
        quoted_pattern = r'On [\d/]+ at [\d:]+ [AaPp][Mm], .+ wrote:'
        has_quotes = bool(re.search(quoted_pattern, content))
        
        # Generate thread ID (using subject + conversation markers)
        thread_components = [subject]
        if has_quotes:
            # Extract timestamp of original message if available
            orig_msg_match = re.search(quoted_pattern, content)
            if orig_msg_match:
                thread_components.append(orig_msg_match.group(0))
                
        return '_'.join(thread_components)
    
    def _build_message_relationships(self, messages: List[Dict]) -> None:
        """
        Establishes parent-child relationships between messages in a thread.
        Modifies messages in place to add relationship links.
        """
        for i, msg in enumerate(messages):
            msg['thread_position'] = i
            msg['has_children'] = False
            
            # Look for parent message references in content
            content = msg.get('content', '')
            parent_refs = re.finditer(r'On (\d{1,2}/\d{1,2}/\d{4} at \d{1,2}:\d{2} [AaPp][Mm])', content)
            
            # Find most recent parent reference
            latest_parent_time = None
            for ref in parent_refs:
                try:
                    ref_time = datetime.strptime(ref.group(1), '%m/%d/%Y at %I:%M %p')
                    if not latest_parent_time or ref_time > latest_parent_time:
                        latest_parent_time = ref_time
                except ValueError:
                    continue
            
            if latest_parent_time:
                # Find parent message
                parent_timestamp = latest_parent_time.isoformat()
                for potential_parent in messages[:i]:  # Only look at earlier messages
                    if potential_parent['timestamp'] == parent_timestamp:
                        msg['parent_id'] = potential_parent['index']
                        potential_parent['has_children'] = True
                        break
    
    def _prepare_output(self) -> Dict:
        """
        Prepares final output structure with threads and metadata.
        """
        # Convert metadata sets to lists for JSON serialization
        for metadata in self.thread_metadata.values():
            metadata['participants'] = list(metadata['participants'])
        
        return {
            'threads': dict(self.threads),
            'metadata': self.thread_metadata,
            'stats': {
                'total_threads': len(self.threads),
                'total_messages': sum(m['message_count'] for m in self.thread_metadata.values()),
                'timestamp': datetime.now().isoformat()
            }
        }