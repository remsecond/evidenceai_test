"""Checkpoint registry to track processing state."""

from datetime import datetime
import json
from pathlib import Path
import os

class CheckpointRegistry:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.registry_file = self.base_dir / 'checkpoint_registry.json'
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Load or create registry with defaults."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file) as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load registry ({str(e)}), creating new one")
            
        return {
            'last_update': datetime.now().isoformat(),
            'current_stage': 'initialization',
            'checkpoints': [],
            'pipeline_status': {
                'messages_processed': 0,
                'threads_identified': 0,
                'success_rate': 0.0,
                'last_issues': []
            }
        }
    
    def update_stage(self, stage: str, status: dict):
        """Update registry with new stage information."""
        self.registry['last_update'] = datetime.now().isoformat()
        self.registry['current_stage'] = stage
        
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'status': status
        }
        self.registry['checkpoints'].append(checkpoint)
        
        self._update_pipeline_status(status)
        self._save_registry()
    
    def _update_pipeline_status(self, status: dict):
        """Update pipeline status metrics."""
        pipeline_status = self.registry['pipeline_status']
        if 'message_count' in status:
            pipeline_status['messages_processed'] = status['message_count']
        if 'thread_count' in status:
            pipeline_status['threads_identified'] = status['thread_count']
        if 'success_rate' in status:
            pipeline_status['success_rate'] = status['success_rate']
        if 'issues' in status:
            pipeline_status['last_issues'] = status['issues']
    
    def _save_registry(self):
        """Save registry to file with backup."""
        # Create backup of existing registry
        if self.registry_file.exists():
            backup_file = self.registry_file.with_suffix('.json.bak')
            try:
                with open(self.registry_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            except Exception as e:
                print(f"Warning: Could not create backup ({str(e)})")
        
        # Save new registry
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {str(e)}")
            if backup_file.exists():
                print("Restoring from backup...")
                backup_file.replace(self.registry_file)
    
    def get_current_status(self) -> dict:
        """Get current pipeline status."""
        return {
            'last_update': self.registry['last_update'],
            'current_stage': self.registry['current_stage'],
            'pipeline_status': self.registry['pipeline_status']
        }
    
    def get_checkpoint_history(self) -> list:
        """Get list of all checkpoints."""
        return self.registry['checkpoints']