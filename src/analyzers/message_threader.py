import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

class MessageThreader:
    """Analyzes message relationships and builds conversation threads"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.conversation_threads = {}
        self.message_lookup = {}
        
    def thread_messages(self, messages: List[Dict]) -> Dict:
        """
        Build conversation threads from messages
        
        Args:
            messages: List of parsed message dictionaries
            
        Returns:
            Dict containing threaded conversations and metadata
        """
        self.logger.info("Starting message threading")
        try:
            # Sort messages by timestamp
            sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
            
            # Build message lookup for quick reference
            for msg in sorted_messages:
                self.message_lookup[msg['index']] = msg
            
            # Identify conversation threads
            for msg in sorted_messages:
                self._process_message(msg)
                
            # Build thread metadata
            thread_metadata = self._build_thread_metadata()
            
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'metadata': thread_metadata,
                'threads': self.conversation_threads
            }
            
            self.logger.info(f"Threading complete. Found {len(self.conversation_threads)} threads")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in message threading: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _process_message(self, message: Dict):
        """Process a single message and determine its thread placement"""
        
        # Extract potential parent references from content
        parent_refs = self._find_parent_references(message)
        
        if parent_refs:
            # This is a reply - add to existing thread
            thread_id = self._get_thread_id(parent_refs[0])
            if thread_id not in self.conversation_threads:
                self.conversation_threads[thread_id] = {
                    'messages': [],
                    'participants': set(),
                    'subject': message.get('subject', ''),
                    'start_time': message['timestamp'],
                    'last_time': message['timestamp']
                }
            thread = self.conversation_threads[thread_id]
        else:
            # This is a new thread
            thread_id = f"thread_{message['index']}"
            self.conversation_threads[thread_id] = {
                'messages': [],
                'participants': set(),
                'subject': message.get('subject', ''),
                'start_time': message['timestamp'],
                'last_time': message['timestamp']
            }
            thread = self.conversation_threads[thread_id]
        
        # Add message to thread
        thread['messages'].append({
            'index': message['index'],
            'parent_refs': parent_refs,
            'content': message['content'],
            'metadata': {
                'sender': message['from'],
                'recipient': message['to'],
                'sent_time': message['timestamp'],
                'viewed_time': message.get('viewed_timestamp'),
                'subject': message.get('subject')
            }
        })
        
        # Update thread metadata
        thread['participants'].add(message['from'])
        thread['participants'].add(message['to'])
        thread['last_time'] = max(thread['last_time'], message['timestamp'])
        
    def _find_parent_references(self, message: Dict) -> List[int]:
        """Find references to parent messages in content"""
        parent_refs = []
        
        # Look for "On [date] at [time], [name] wrote:" pattern
        content = message.get('content', '')
        if 'wrote:' in content:
            # Extract potential message indices from references
            # This is a simplified version - could be enhanced with more robust parsing
            for i in range(1, len(self.message_lookup) + 1):
                if str(i) in content and i < message['index']:
                    parent_refs.append(i)
                    
        return parent_refs
        
    def _get_thread_id(self, parent_ref: int) -> str:
        """Get thread ID for a parent reference"""
        # Find the root thread that contains this parent
        for thread_id, thread in self.conversation_threads.items():
            for msg in thread['messages']:
                if msg['index'] == parent_ref:
                    return thread_id
        return f"thread_{parent_ref}"
        
    def _build_thread_metadata(self) -> Dict:
        """Build metadata about all threads"""
        return {
            'total_threads': len(self.conversation_threads),
            'total_messages': sum(len(t['messages']) for t in self.conversation_threads.values()),
            'thread_stats': {
                thread_id: {
                    'message_count': len(thread['messages']),
                    'participant_count': len(thread['participants']),
                    'duration': (datetime.fromisoformat(thread['last_time']) - 
                               datetime.fromisoformat(thread['start_time'])).total_seconds(),
                    'subject': thread['subject']
                }
                for thread_id, thread in self.conversation_threads.items()
            }
        }