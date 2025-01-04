import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class CheckpointManager:
    def __init__(self, session_dir: Path):
        self.session_dir = Path(session_dir)
        self.checkpoint_file = self.session_dir / "pipeline_checkpoint.json"
        self.start_time = time.time()
        self.max_duration = 3600  # 1 hour
        
    def save_checkpoint(self, stage: str, data: Dict[str, Any]) -> None:
        checkpoint = {
            'stage': stage,
            'timestamp': time.time(),
            'data': data
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
            
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return None
        
    def time_remaining(self) -> float:
        return self.max_duration - (time.time() - self.start_time)
        
    def should_finalize(self) -> bool:
        return self.time_remaining() < 300  # 5 minutes warning