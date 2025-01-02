"""Message threading and chain building module."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set
import re
import json

@dataclass
class ThreadMetadata:
    """Thread metadata container."""
    thread_id: str
    start_time: datetime
    last_update: datetime
    participants: Set[str] = field(default_factory=set)
    message_count: int = 0
    depth: int = 0
    subject: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['last_update'] = self.last_update.isoformat()
        data['participants'] = list(self.participants)
        return data

class ThreadEncoder(json.JSONEncoder):
    """JSON encoder for thread data."""
    def default(self, obj):
        if isinstance(obj, ThreadMetadata):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

class MessageThreader:
    """Handles message threading and conversation reconstruction."""
    
    def __init__(self):
        self.threads = {}
        self.thread_metadata = {}
        self._message_map = {}
    
    def process_messages(self, messages: List[Dict]) -> Dict[str, Dict]:
        """Process messages into threaded conversations."""
        try:
            # First pass: Create message map
            for msg in messages:
                msg_id = self._generate_message_id(msg)
                if msg_id:  # Only process valid messages
                    self._message_map[msg_id] = msg
            
            # Second pass: Build thread relationships
            for msg_id, msg in self._message_map.items():
                parent_id = self._find_parent_message(msg)
                if parent_id:
                    if 'children' not in self._message_map[parent_id]:
                        self._message_map[parent_id]['children'] = []
                    self._message_map[parent_id]['children'].append(msg)
                    msg['parent_id'] = parent_id
                else:
                    # No parent - this is a thread root
                    thread_id = self._generate_thread_id(msg)
                    self.threads[thread_id] = msg
            
            # Third pass: Build metadata
            self._build_thread_metadata()
            
            return self.threads
            
        except Exception as e:
            print(f"Error processing messages: {str(e)}")
            return {}
    
    def _generate_message_id(self, msg: Dict) -> Optional[str]:
        """Generate unique message identifier."""
        if not msg.get('timestamp') or not msg.get('from'):
            return None
        timestamp = msg['timestamp'].replace(':', '').replace('-', '')
        return f"{msg['from']}_{timestamp}"
    
    def _generate_thread_id(self, msg: Dict) -> str:
        """Generate unique thread identifier."""
        subject = msg.get('subject', '').strip()
        clean_subject = re.sub(r'[^a-zA-Z0-9]', '', subject) if subject else 'no_subject'
        timestamp = msg['timestamp'].replace(':', '').replace('-', '')
        return f"thread_{clean_subject}_{timestamp}"
    
    def _find_parent_message(self, msg: Dict) -> Optional[str]:
        """Find parent message based on content and timing."""
        # Look for quoted content references
        quoted_pattern = r'On (.*?), (.*?) wrote:'
        matches = re.findall(quoted_pattern, msg.get('content', ''))
        
        if matches:
            # For each potential parent reference
            for date_str, sender in matches:
                try:
                    # Convert reference date to datetime
                    ref_date = datetime.strptime(date_str, '%m/%d/%Y at %I:%M %p')
                    ref_iso = ref_date.isoformat()
                    
                    # Look for matching message
                    for msg_id, candidate in self._message_map.items():
                        if (candidate['from'] == sender and 
                            candidate['timestamp'] == ref_iso and
                            candidate['timestamp'] < msg['timestamp']):
                            return msg_id
                except ValueError:
                    continue
        
        # Try subject matching if no quote found
        if subject := msg.get('subject'):
            # Remove Re: and clean subject
            clean_subject = re.sub(r'^[Rr][Ee]:\s*', '', subject).strip()
            potential_parents = [
                (mid, m) for mid, m in self._message_map.items()
                if (m['timestamp'] < msg['timestamp'] and
                    re.sub(r'^[Rr][Ee]:\s*', '', m.get('subject', '')).strip() == clean_subject)
            ]
            
            if potential_parents:
                # Get most recent matching subject
                return max(potential_parents, key=lambda x: x[1]['timestamp'])[0]
        
        return None
    
    def _build_thread_metadata(self):
        """Build metadata for all threads."""
        for thread_id, root in self.threads.items():
            start_time = datetime.fromisoformat(root['timestamp'])
            metadata = ThreadMetadata(
                thread_id=thread_id,
                start_time=start_time,
                last_update=start_time,
                participants={root['from'], root['to']}
            )
            
            def process_message(msg, depth=0):
                metadata.message_count += 1
                metadata.depth = max(metadata.depth, depth)
                if msg.get('timestamp'):
                    update_time = datetime.fromisoformat(msg['timestamp'])
                    metadata.last_update = max(metadata.last_update, update_time)
                metadata.participants.add(msg['from'])
                metadata.participants.add(msg['to'])
                
                for child in msg.get('children', []):
                    process_message(child, depth + 1)
            
            process_message(root)
            metadata.subject = root.get('subject')
            self.thread_metadata[thread_id] = metadata
    
    def get_thread_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all threads."""
        return {k: v.to_dict() for k, v in self.thread_metadata.items()}
    
    def get_thread_statistics(self) -> Dict:
        """Calculate statistics across all threads."""
        if not self.thread_metadata:
            return {}
            
        total_messages = sum(m.message_count for m in self.thread_metadata.values())
        total_participants = len(set().union(
            *[m.participants for m in self.thread_metadata.values()]
        ))
        
        metadata_list = list(self.thread_metadata.values())
        return {
            'total_threads': len(self.threads),
            'total_messages': total_messages,
            'total_participants': total_participants,
            'avg_thread_depth': sum(m.depth for m in metadata_list) / len(metadata_list),
            'avg_messages_per_thread': total_messages / len(self.threads),
            'time_span': {
                'start': min(m.start_time for m in metadata_list).isoformat(),
                'end': max(m.last_update for m in metadata_list).isoformat()
            }
        }