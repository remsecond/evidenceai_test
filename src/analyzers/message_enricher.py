import logging
from datetime import datetime
from typing import Dict, List, Optional

class MessageEnricher:
    """Enriches messages with metadata without altering core content"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
    def enrich_messages(self, messages: List[Dict]) -> Dict:
        """
        Add metadata and relationships to messages while preserving original content
        
        Args:
            messages: List of parsed message dictionaries
            
        Returns:
            Dict containing enriched messages with metadata
        """
        try:
            enriched_data = {
                'metadata': {
                    'total_messages': len(messages),
                    'date_range': self._get_date_range(messages),
                    'participants': self._get_participants(messages)
                },
                'messages': [
                    self._enrich_message(msg, messages) 
                    for msg in sorted(messages, key=lambda x: x['timestamp'])
                ],
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Enriched {len(messages)} messages")
            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Error enriching messages: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _enrich_message(self, message: Dict, all_messages: List[Dict]) -> Dict:
        """Add metadata to a single message"""
        enriched = {
            # Preserve original data
            'original': message,
            
            # Add objective metadata
            'metadata': {
                'index': message['index'],
                'timestamps': {
                    'sent': message['timestamp'],
                    'viewed': message.get('viewed_timestamp'),
                    'response_time': self._get_response_time(message) if message.get('viewed_timestamp') else None
                },
                'participants': {
                    'sender': message['from'],
                    'recipient': message['to']
                },
                'references': self._find_references(message, all_messages)
            }
        }
        
        return enriched

    def _get_date_range(self, messages: List[Dict]) -> Dict:
        """Get the date range of messages"""
        timestamps = [msg['timestamp'] for msg in messages if msg.get('timestamp')]
        if not timestamps:
            return {'start': None, 'end': None}
            
        return {
            'start': min(timestamps),
            'end': max(timestamps)
        }

    def _get_participants(self, messages: List[Dict]) -> Dict:
        """Get unique participants and their roles"""
        participants = {
            'senders': set(msg['from'] for msg in messages if msg.get('from')),
            'recipients': set(msg['to'] for msg in messages if msg.get('to'))
        }
        
        return {
            'unique_participants': list(participants['senders'] | participants['recipients']),
            'sender_count': len(participants['senders']),
            'recipient_count': len(participants['recipients'])
        }

    def _get_response_time(self, message: Dict) -> Optional[float]:
        """Calculate response time in seconds if available"""
        try:
            if message.get('timestamp') and message.get('viewed_timestamp'):
                sent = datetime.fromisoformat(message['timestamp'])
                viewed = datetime.fromisoformat(message['viewed_timestamp'])
                return (viewed - sent).total_seconds()
        except Exception as e:
            self.logger.warning(f"Could not calculate response time: {str(e)}")
        return None

    def _find_references(self, message: Dict, all_messages: List[Dict]) -> Dict:
        """Find objective references to other messages"""
        references = {
            'quoted_content': [],  # Store quoted text without interpretation
            'temporal_refs': []    # Store temporal markers 
        }
        
        content = message.get('content', '')
        
        # Look for quote patterns without interpretation
        if 'wrote:' in content:
            # Extract quoted text
            quotes = content.split('wrote:')[1:]
            references['quoted_content'] = [q.strip() for q in quotes]
            
        # Look for temporal references
        if 'On' in content and 'at' in content:
            # Extract temporal markers
            refs = [line for line in content.split('\n') 
                   if line.strip().startswith('On') and 'at' in line]
            references['temporal_refs'] = refs
            
        return references