import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class LLMFormatter:
    """Format parsed OFW messages for LLM processing"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.output_dir = self.base_dir / "output" / "llm_formatted"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def format_messages(self, messages: List[Dict]) -> Dict:
        """Format messages for LLM processing"""
        try:
            formatted = {
                'metadata': self._create_metadata(messages),
                'threads': self._group_threads(messages),
                'statistics': self._calculate_stats(messages),
                'formatted_at': datetime.now().isoformat()
            }
            
            self._save_formatted(formatted)
            return formatted
            
        except Exception as e:
            print(f"Error formatting messages: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_metadata(self, messages: List[Dict]) -> Dict:
        """Create metadata about the message set"""
        return {
            'total_messages': len(messages),
            'date_range': {
                'start': min(m['timestamp'] for m in messages if m.get('timestamp')),
                'end': max(m['timestamp'] for m in messages if m.get('timestamp'))
            },
            'participants': self._extract_participants(messages)
        }
    
    def _extract_participants(self, messages: List[Dict]) -> Dict:
        """Extract unique participants from messages"""
        senders = set(m['from'] for m in messages if m.get('from'))
        recipients = set(m['to'] for m in messages if m.get('to'))
        
        return {
            'unique_participants': sorted(senders | recipients),
            'senders': sorted(senders),
            'recipients': sorted(recipients)
        }
    
    def _group_threads(self, messages: List[Dict]) -> List[Dict]:
        """Group messages into conversation threads"""
        # Sort messages by timestamp
        sorted_msgs = sorted(
            messages,
            key=lambda x: x.get('timestamp', '9999-12-31')
        )
        
        # Group by subject
        threads = {}
        for msg in sorted_msgs:
            subject = msg.get('subject', '').strip()
            if not subject:
                subject = '[No Subject]'
            
            if subject not in threads:
                threads[subject] = {
                    'subject': subject,
                    'messages': [],
                    'participants': set(),
                    'start_time': msg.get('timestamp'),
                    'last_time': msg.get('timestamp')
                }
            
            thread = threads[subject]
            thread['messages'].append(msg)
            thread['participants'].add(msg.get('from'))
            thread['participants'].add(msg.get('to'))
            thread['last_time'] = msg.get('timestamp')
        
        # Convert to list and clean up
        return [
            {
                'subject': t['subject'],
                'messages': t['messages'],
                'participants': sorted(p for p in t['participants'] if p),
                'message_count': len(t['messages']),
                'start_time': t['start_time'],
                'last_time': t['last_time']
            }
            for t in threads.values()
        ]
    
    def _calculate_stats(self, messages: List[Dict]) -> Dict:
        """Calculate various statistics about the messages"""
        return {
            'message_counts': {
                'total': len(messages),
                'by_sender': self._count_by_field(messages, 'from'),
                'by_day': self._count_by_day(messages)
            },
            'response_times': self._calculate_response_times(messages),
            'thread_statistics': self._thread_stats(messages)
        }
    
    def _count_by_field(self, messages: List[Dict], field: str) -> Dict:
        """Count messages by a specific field"""
        counts = {}
        for msg in messages:
            value = msg.get(field)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _count_by_day(self, messages: List[Dict]) -> Dict:
        """Count messages by day"""
        counts = {}
        for msg in messages:
            if msg.get('timestamp'):
                day = msg['timestamp'][:10]  # YYYY-MM-DD
                counts[day] = counts.get(day, 0) + 1
        return counts
    
    def _calculate_response_times(self, messages: List[Dict]) -> Dict:
        """Calculate response time statistics"""
        response_times = []
        
        # Sort messages by timestamp
        sorted_msgs = sorted(
            messages,
            key=lambda x: x.get('timestamp', '9999-12-31')
        )
        
        # Calculate time between messages in same thread
        for i in range(1, len(sorted_msgs)):
            curr = sorted_msgs[i]
            prev = sorted_msgs[i-1]
            
            if (curr.get('subject') == prev.get('subject') and
                curr.get('timestamp') and prev.get('timestamp')):
                try:
                    curr_time = datetime.fromisoformat(curr['timestamp'])
                    prev_time = datetime.fromisoformat(prev['timestamp'])
                    delta = (curr_time - prev_time).total_seconds() / 3600  # hours
                    response_times.append(delta)
                except:
                    continue
        
        if not response_times:
            return {}
            
        return {
            'average_hours': sum(response_times) / len(response_times),
            'min_hours': min(response_times),
            'max_hours': max(response_times)
        }
    
    def _thread_stats(self, messages: List[Dict]) -> Dict:
        """Calculate statistics about conversation threads"""
        threads = self._group_threads(messages)
        
        return {
            'total_threads': len(threads),
            'avg_messages_per_thread': sum(t['message_count'] for t in threads) / len(threads) if threads else 0,
            'longest_thread': max((t['message_count'] for t in threads), default=0),
            'thread_subjects': [t['subject'] for t in threads]
        }
    
    def _save_formatted(self, formatted: Dict) -> None:
        """Save formatted output to file"""
        output_file = self.output_dir / f'formatted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, indent=2)
        print(f"Saved formatted output to {output_file}")