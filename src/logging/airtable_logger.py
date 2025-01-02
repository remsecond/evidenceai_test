"""Airtable logging module."""

from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class AirtableLogger:
    """Logs threading operations to Airtable."""
    
    def __init__(self, base_id: Optional[str] = None, api_key: Optional[str] = None):
        self.base_id = base_id
        self.api_key = api_key
        self.pending_records = []
        self._setup_local_storage()
    
    def _setup_local_storage(self):
        """Setup local storage for offline operation."""
        self.storage_dir = Path('airtable_queue')
        self.storage_dir.mkdir(exist_ok=True)
    
    def log_processing(self, file_id: str, results: Dict):
        """Log processing results."""
        record = {
            'file_id': file_id,
            'timestamp': datetime.now().isoformat(),
            'record_type': 'processing',
            'status': results['status'],
            'message_count': results.get('statistics', {}).get('messages', 0),
            'thread_count': results.get('statistics', {}).get('threads', 0),
            'processing_time': results.get('processing_time'),
            'validation_status': results.get('stages', {}).get('validation', {}).get('status')
        }
        self._queue_record('Processing_Log', record)
    
    def log_validation(self, file_id: str, validation: Dict):
        """Log validation results."""
        record = {
            'file_id': file_id,
            'timestamp': datetime.now().isoformat(),
            'record_type': 'validation',
            'valid': validation.get('valid', False),
            'error_count': len(validation.get('errors', [])),
            'warning_count': len(validation.get('warnings', [])),
            'stats': json.dumps(validation.get('stats', {}))
        }
        self._queue_record('Validation_Log', record)
    
    def log_metadata(self, file_id: str, metadata: Dict):
        """Log enhanced metadata."""
        record = {
            'file_id': file_id,
            'timestamp': datetime.now().isoformat(),
            'record_type': 'metadata',
            'thread_count': len(metadata),
            'total_participants': len(set().union(*[
                set(m.get('participants', [])) 
                for m in metadata.values()
                if isinstance(m, dict)
            ])) if metadata else 0,
            'metadata_summary': json.dumps({
                k: {
                    'message_count': v.get('message_count', 0),
                    'depth': v.get('depth', 0)
                }
                for k, v in metadata.items()
                if isinstance(v, dict)
            })
        }
        self._queue_record('Metadata_Log', record)
    
    def _queue_record(self, table: str, record: Dict):
        """Queue a record for later sending to Airtable."""
        self.pending_records.append({
            'table': table,
            'record': record
        })
        
        # If we have Airtable credentials, try to sync immediately
        if self.base_id and self.api_key:
            self.sync()
        else:
            self._store_locally()
    
    def sync(self) -> bool:
        """Sync pending records to Airtable or store locally."""
        if not self.pending_records:
            return True
            
        if not (self.base_id and self.api_key):
            return self._store_locally()
            
        try:
            # TODO: Implement Airtable API integration
            # For now, store locally
            return self._store_locally()
        except Exception as e:
            print(f"Error syncing to Airtable: {str(e)}")
            return self._store_locally()
    
    def _store_locally(self) -> bool:
        """Store pending records locally for later sync."""
        if not self.pending_records:
            return True
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.storage_dir / f"pending_records_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.pending_records, f, indent=2)
            
            self.pending_records = []
            return True
            
        except Exception as e:
            print(f"Error storing records locally: {str(e)}")
            return False