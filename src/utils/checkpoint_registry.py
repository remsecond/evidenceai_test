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
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {
            'last_update': None,
            'current_stage': None,
            'checkpoints': [],
            'pipeline_status': {
                'messages_processed': 0,
                'threads_identified': 0,
                'success_rate': 0.0,
                'last_issues': []
            }
        }
    
    def update_stage(self, stage: str, status: dict):
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
        if 'message_count' in status:
            self.registry['pipeline_status']['messages_processed'] = status['message_count']
        if 'thread_count' in status:
            self.registry['pipeline_status']['threads_identified'] = status['thread_count']
        if 'success_rate' in status:
            self.registry['pipeline_status']['success_rate'] = status['success_rate']
        if 'issues' in status:
            self.registry['pipeline_status']['last_issues'] = status['issues']
    
    def _save_registry(self):
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def get_current_status(self) -> dict:
        return {
            'last_update': self.registry['last_update'],
            'current_stage': self.registry['current_stage'],
            'pipeline_status': self.registry['pipeline_status']
        }
    
    def get_checkpoint_history(self) -> list:
        return self.registry['checkpoints']