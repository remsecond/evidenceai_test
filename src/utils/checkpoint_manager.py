import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil
import hashlib

class CheckpointManager:
    """Manages checkpoint creation, verification, and restoration"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parents[2]
        self.checkpoint_dir = self.base_dir / "output" / "checkpoints"
        self.backup_dir = self.checkpoint_dir / "backups"
        
        # Ensure directories exist
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize checkpoint registry
        self.registry_file = self.checkpoint_dir / "checkpoint_registry.json"
        self.registry = self._load_registry()
        
    def save_checkpoint(self, stage: str, data: Dict, metadata: Optional[Dict] = None) -> Path:
        """Save a new checkpoint with verification"""
        # Create checkpoint data structure
        checkpoint = {
            'stage': stage,
            'data': data,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'previous_checkpoint': self.get_latest_checkpoint_id(stage)
        }
        
        # Generate unique identifier
        checkpoint_id = self._generate_checkpoint_id(checkpoint)
        checkpoint['checkpoint_id'] = checkpoint_id
        
        # Add checksum
        checkpoint['checksum'] = self._calculate_checksum(checkpoint)
        
        # Save checkpoint
        checkpoint_file = self.checkpoint_dir / f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Backup previous checkpoint if it exists
        self._backup_previous_checkpoint(stage)
        
        # Save new checkpoint
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        # Update registry
        self._update_registry(checkpoint_id, checkpoint_file, stage)
        
        return checkpoint_file
    
    def load_checkpoint(self, stage: str = None, checkpoint_id: str = None) -> Optional[Dict]:
        """Load checkpoint with verification"""
        checkpoint_file = self._find_checkpoint(stage, checkpoint_id)
        if not checkpoint_file:
            return None
            
        try:
            with open(checkpoint_file) as f:
                checkpoint = json.load(f)
            
            # Verify checksum
            stored_checksum = checkpoint.pop('checksum')
            calculated_checksum = self._calculate_checksum(checkpoint)
            
            if stored_checksum != calculated_checksum:
                raise ValueError(f"Checkpoint {checkpoint_file} failed verification!")
                
            checkpoint['checksum'] = stored_checksum
            return checkpoint
            
        except Exception as e:
            print(f"Error loading checkpoint: {str(e)}")
            # Attempt to restore from backup
            restored = self._restore_from_backup(stage)
            if restored:
                print(f"Restored from backup: {restored}")
                return self.load_checkpoint(stage)
            return None
    
    def get_latest_checkpoint_id(self, stage: Optional[str] = None) -> Optional[str]:
        """Get the ID of the latest checkpoint for a stage"""
        checkpoints = [cp for cp in self.registry.values() if not stage or cp['stage'] == stage]
        if not checkpoints:
            return None
            
        return max(checkpoints, key=lambda x: x['timestamp'])['checkpoint_id']
    
    def verify_all_checkpoints(self) -> Tuple[List[Path], List[Path]]:
        """Verify all checkpoints and return lists of valid and invalid files"""
        valid_files = []
        invalid_files = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            if checkpoint_file.name == "checkpoint_registry.json":
                continue
                
            try:
                with open(checkpoint_file) as f:
                    checkpoint = json.load(f)
                
                stored_checksum = checkpoint.get('checksum')
                if not stored_checksum:
                    invalid_files.append(checkpoint_file)
                    continue
                
                checkpoint_copy = checkpoint.copy()
                checkpoint_copy.pop('checksum')
                calculated_checksum = self._calculate_checksum(checkpoint_copy)
                
                if stored_checksum == calculated_checksum:
                    valid_files.append(checkpoint_file)
                else:
                    invalid_files.append(checkpoint_file)
                    
            except Exception:
                invalid_files.append(checkpoint_file)
        
        return valid_files, invalid_files
    
    def get_chain_of_checkpoints(self, stage: str) -> List[Dict]:
        """Get the complete chain of checkpoints for a stage"""
        stage_checkpoints = []
        current_id = self.get_latest_checkpoint_id(stage)
        
        while current_id:
            checkpoint = self.load_checkpoint(checkpoint_id=current_id)
            if not checkpoint:
                break
                
            stage_checkpoints.insert(0, checkpoint)
            current_id = checkpoint.get('previous_checkpoint')
            
        return stage_checkpoints
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback to a specific checkpoint"""
        if checkpoint_id not in self.registry:
            return False
            
        checkpoint_info = self.registry[checkpoint_id]
        checkpoint_file = Path(checkpoint_info['file'])
        stage = checkpoint_info['stage']
        
        # Verify checkpoint is valid
        checkpoint = self.load_checkpoint(checkpoint_id=checkpoint_id)
        if not checkpoint:
            return False
            
        # Move current checkpoint to backup
        self._backup_previous_checkpoint(stage)
        
        # Update registry to mark this as latest
        for cp_id, info in list(self.registry.items()):
            if (info['stage'] == stage and 
                info['timestamp'] > checkpoint_info['timestamp']):
                del self.registry[cp_id]
        
        self._save_registry()
        return True
    
    def get_stage_status(self, stage: str) -> Dict:
        """Get detailed status information for a stage"""
        checkpoints = self.get_chain_of_checkpoints(stage)
        if not checkpoints:
            return {
                'status': 'not_started',
                'checkpoint_count': 0,
                'last_updated': None,
                'chain_complete': True,
                'chain_length': 0
            }
            
        # Verify chain is complete
        chain_complete = True
        for i, cp in enumerate(checkpoints[1:], 1):
            if cp['previous_checkpoint'] != checkpoints[i-1]['checkpoint_id']:
                chain_complete = False
                break
                
        return {
            'status': 'in_progress',
            'checkpoint_count': len(checkpoints),
            'last_updated': checkpoints[-1]['timestamp'],
            'chain_complete': chain_complete,
            'chain_length': len(checkpoints),
            'latest_id': checkpoints[-1]['checkpoint_id']
        }
    
    def prune_old_checkpoints(self, max_per_stage: int = 5) -> None:
        """Remove old checkpoints keeping only the specified number per stage"""
        stage_files = {}
        
        # Group files by stage
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            if checkpoint_file.name == "checkpoint_registry.json":
                continue
                
            stage = checkpoint_file.name.split('_')[0]
            if stage not in stage_files:
                stage_files[stage] = []
            stage_files[stage].append(checkpoint_file)
            
        # Keep only the most recent files for each stage
        for stage, files in stage_files.items():
            sorted_files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
            files_to_remove = sorted_files[max_per_stage:]
            
            for file in files_to_remove:
                # Move to backup instead of deleting
                backup_file = self.backup_dir / f"pruned_{file.name}"
                shutil.move(file, backup_file)
                
                # Update registry
                self._remove_from_registry(file)
    
    def _generate_checkpoint_id(self, checkpoint: Dict) -> str:
        """Generate unique identifier for checkpoint"""
        components = [
            checkpoint['stage'],
            checkpoint['timestamp'],
            str(hash(str(checkpoint['data'])))
        ]
        return hashlib.sha256(''.join(components).encode()).hexdigest()[:12]
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate checksum of checkpoint data"""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def _backup_previous_checkpoint(self, stage: str) -> None:
        """Backup the previous checkpoint for a stage"""
        previous_files = list(self.checkpoint_dir.glob(f"{stage}_*.json"))
        if not previous_files:
            return
            
        latest_file = max(previous_files, key=lambda p: p.stat().st_mtime)
        backup_file = self.backup_dir / f"backup_{latest_file.name}"
        shutil.copy2(latest_file, backup_file)
    
    def _find_checkpoint(self, stage: Optional[str], checkpoint_id: Optional[str]) -> Optional[Path]:
        """Find checkpoint file by stage or ID"""
        if checkpoint_id and checkpoint_id in self.registry:
            return Path(self.registry[checkpoint_id]['file'])
            
        if stage:
            # Find latest checkpoint for stage
            checkpoints = [cp for cp in self.registry.values() if cp['stage'] == stage]
            if checkpoints:
                return Path(max(checkpoints, key=lambda x: x['timestamp'])['file'])
        
        return None
    
    def _restore_from_backup(self, stage: str) -> Optional[Path]:
        """Attempt to restore from backup"""
        backup_files = list(self.backup_dir.glob(f"backup_{stage}_*.json"))
        if not backup_files:
            return None
            
        latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
        restore_file = self.checkpoint_dir / latest_backup.name[6:]  # Remove 'backup_' prefix
        shutil.copy2(latest_backup, restore_file)
        return restore_file
    
    def _load_registry(self) -> Dict:
        """Load checkpoint registry"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_registry(self) -> None:
        """Save checkpoint registry"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _update_registry(self, checkpoint_id: str, checkpoint_file: Path, stage: str) -> None:
        """Update checkpoint registry"""
        self.registry[checkpoint_id] = {
            'file': str(checkpoint_file),
            'stage': stage,
            'timestamp': datetime.now().isoformat()
        }
        self._save_registry()
    
    def _remove_from_registry(self, checkpoint_file: Path) -> None:
        """Remove a checkpoint from the registry"""
        ids_to_remove = [
            cp_id for cp_id, info in self.registry.items()
            if info['file'] == str(checkpoint_file)
        ]
        
        for cp_id in ids_to_remove:
            del self.registry[cp_id]
            
        self._save_registry()