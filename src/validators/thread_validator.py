"""Validation module for message threading."""

from datetime import datetime
from typing import Dict, List
import logging

class ThreadValidator:
    """Validates thread structures and relationships."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_threading_results(self, threads: Dict, metadata: Dict) -> Dict:
        """Validate complete threading results."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_threads': len(threads),
                'total_messages': 0,
                'max_depth': 0
            }
        }
        
        # Track participants across all threads
        all_participants = set()
        
        # Validate each thread
        for thread_id, root_node in threads.items():
            # Validate thread structure
            structure_errors = self.validate_thread_structure(root_node)
            if structure_errors:
                validation_results['valid'] = False
                validation_results['errors'].extend(
                    f"Thread {thread_id}: {error}" 
                    for error in structure_errors
                )
            
            # Validate thread metadata
            if thread_id in metadata:
                meta_errors = self.validate_thread_metadata(metadata[thread_id])
                if meta_errors:
                    validation_results['valid'] = False
                    validation_results['errors'].extend(
                        f"Thread {thread_id} metadata: {error}" 
                        for error in meta_errors
                    )
                
                # Update statistics
                validation_results['stats']['total_messages'] += metadata[thread_id]['message_count']
                validation_results['stats']['max_depth'] = max(
                    validation_results['stats']['max_depth'],
                    metadata[thread_id]['depth']
                )
                all_participants.update(metadata[thread_id]['participants'])
            else:
                validation_results['errors'].append(f"Missing metadata for thread {thread_id}")
                validation_results['valid'] = False
        
        # Add participant statistics
        validation_results['stats']['total_participants'] = len(all_participants)
        
        # Add warnings for potential issues
        if validation_results['stats']['max_depth'] > 10:
            validation_results['warnings'].append("Unusually deep thread detected")
        
        return validation_results
    
    def validate_thread_structure(self, thread_root: Dict, visited=None) -> List[str]:
        """Validate a thread's structure."""
        errors = []
        if visited is None:
            visited = set()
        
        # Check for cycles
        if thread_root['timestamp'] in visited:
            errors.append(f"Circular reference detected: {thread_root['timestamp']}")
            return errors
        
        visited.add(thread_root['timestamp'])
        
        # Validate each child
        for child in thread_root.get('children', []):
            # Child's timestamp should be after parent's
            try:
                parent_time = datetime.fromisoformat(thread_root['timestamp'])
                child_time = datetime.fromisoformat(child['timestamp'])
                if child_time <= parent_time:
                    errors.append(
                        f"Invalid timestamp order: child {child['timestamp']} "
                        f"is before parent {thread_root['timestamp']}"
                    )
            except ValueError as e:
                errors.append(f"Invalid timestamp format: {str(e)}")
            
            # Child should reference correct parent
            if child.get('parent_id') != self._generate_message_id(thread_root):
                errors.append(
                    f"Invalid parent reference for message at {child['timestamp']}"
                )
            
            # Recursively validate children
            errors.extend(self.validate_thread_structure(child, visited))
        
        return errors
    
    def validate_thread_metadata(self, metadata: Dict) -> List[str]:
        """Validate thread metadata."""
        errors = []
        
        # Required metadata fields
        required_fields = ['thread_id', 'message_count', 'depth']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        if not errors:
            # Validate counts
            if metadata['message_count'] < 1:
                errors.append("Invalid message count")
            if metadata['depth'] < 0:
                errors.append("Invalid thread depth")
            
            # Validate participants
            if not metadata.get('participants'):
                errors.append("Empty participants set")
        
        return errors
    
    def _generate_message_id(self, msg: Dict) -> str:
        """Generate message identifier for validation."""
        timestamp = msg['timestamp'].replace(':', '').replace('-', '')
        return f"{msg['from']}_{timestamp}"