import logging
from datetime import datetime
from typing import Dict, List, Set

class RelationshipDetector:
    """Detects message relationships without interpretation"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
    def detect_relationships(self, enriched_data: Dict) -> Dict:
        """
        Identify objective relationships between messages
        
        Args:
            enriched_data: Dictionary containing enriched messages
            
        Returns:
            Dict containing relationship data
        """
        try:
            # Extract messages
            messages = enriched_data['messages']
            
            # Build relationship maps
            relationships = {
                'temporal': self._map_temporal_relationships(messages),
                'reference': self._map_references(messages),
                'participant': self._map_participant_interactions(messages)
            }
            
            result = {
                'metadata': {
                    'relationship_types': list(relationships.keys()),
                    'timestamp': datetime.now().isoformat()
                },
                'relationships': relationships,
                'status': 'success'
            }
            
            self.logger.info("Completed relationship detection")
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting relationships: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _map_temporal_relationships(self, messages: List[Dict]) -> Dict:
        """Map time-based relationships between messages"""
        temporal_map = {
            'sequence': [],           # Messages in temporal order
            'same_day_groups': {},    # Messages grouped by date
            'response_patterns': []    # Pairs of messages with response times
        }
        
        # Create temporal sequence
        sorted_msgs = sorted(messages, 
                           key=lambda x: x['original']['timestamp'])
        temporal_map['sequence'] = [msg['metadata']['index'] for msg in sorted_msgs]
        
        # Group by date
        for msg in messages:
            date = msg['original']['timestamp'].split('T')[0]
            if date not in temporal_map['same_day_groups']:
                temporal_map['same_day_groups'][date] = []
            temporal_map['same_day_groups'][date].append(msg['metadata']['index'])
            
        # Map response patterns
        for msg in messages:
            if msg['metadata']['timestamps'].get('response_time'):
                temporal_map['response_patterns'].append({
                    'message_id': msg['metadata']['index'],
                    'response_time': msg['metadata']['timestamps']['response_time']
                })
                
        return temporal_map

    def _map_references(self, messages: List[Dict]) -> Dict:
        """Map explicit references between messages"""
        reference_map = {
            'quote_references': [],    # Messages containing quotes
            'temporal_references': []  # Messages with temporal markers
        }
        
        for msg in messages:
            refs = msg['metadata']['references']
            
            # Map quote references
            if refs['quoted_content']:
                reference_map['quote_references'].append({
                    'message_id': msg['metadata']['index'],
                    'quote_count': len(refs['quoted_content'])
                })
                
            # Map temporal references
            if refs['temporal_refs']:
                reference_map['temporal_references'].append({
                    'message_id': msg['metadata']['index'],
                    'reference_count': len(refs['temporal_refs'])
                })
                
        return reference_map

    def _map_participant_interactions(self, messages: List[Dict]) -> Dict:
        """Map message exchanges between participants"""
        interaction_map = {
            'direct_exchanges': [],     # Direct message pairs
            'participant_activity': {}  # Messages per participant
        }
        
        # Map direct exchanges
        for msg in messages:
            interaction_map['direct_exchanges'].append({
                'message_id': msg['metadata']['index'],
                'from': msg['metadata']['participants']['sender'],
                'to': msg['metadata']['participants']['recipient']
            })
            
        # Map participant activity
        for msg in messages:
            sender = msg['metadata']['participants']['sender']
            if sender not in interaction_map['participant_activity']:
                interaction_map['participant_activity'][sender] = []
            interaction_map['participant_activity'][sender].append(
                msg['metadata']['index']
            )
            
        return interaction_map