from pathlib import Path
import json
from datetime import datetime
from enum import Enum, auto

class DevelopmentStage(Enum):
    SETUP = auto()
    PDF_PARSER = auto()
    THREADING = auto()
    RELATIONSHIPS = auto()
    TOPICS = auto()
    COMPLETE = auto()

class WorkflowManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.output_dir = self.base_dir / "output"
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.status_file = self.base_dir / "src" / "project_status.json"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.load_status()
    
    def load_status(self):
        try:
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        except FileNotFoundError:
            self.create_initial_status()
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        self.implementation_status = self._get_implementation_status()
    
    def _get_implementation_status(self):
        return {
            'pdf_parser': self.status['project_overview']['modules']['parsing']['status'],
            'threading': self.status['project_overview']['modules']['threading']['status'],
            'relationships': self.status['project_overview']['modules']['relationship_analysis']['status'],
            'topics': self.status['project_overview']['modules']['topic_detection']['status']
        }
    
    def print_status(self):
        print("\nModule Implementation Status:")
        for module, status in self.implementation_status.items():
            symbol = "✓" if status == "complete" else "-"
            print(f"{symbol} {module}: {status}")
    
    def save_checkpoint(self, stage, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{stage}_{timestamp}.json"
        
        save_data = {
            "stage": stage,
            "timestamp": timestamp,
            "data": data,
            "status": self.implementation_status
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
            
        print(f"Checkpoint saved: {checkpoint_file.name}")
        return checkpoint_file
    
    def get_last_checkpoint(self):
        checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.json"))
        if not checkpoints:
            return None, None
            
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        with open(latest) as f:
            data = json.load(f)
        return latest, data
    
    def create_initial_status(self):
        initial_status = {
            "project_overview": {
                "name": "EvidenceAI",
                "current_phase": DevelopmentStage.PDF_PARSER.name,
                "modules": {
                    "parsing": {
                        "status": "in_progress",
                        "current_focus": True
                    },
                    "threading": {
                        "status": "pending",
                        "current_focus": False
                    },
                    "relationship_analysis": {
                        "status": "pending",
                        "current_focus": False
                    },
                    "topic_detection": {
                        "status": "pending",
                        "current_focus": False
                    }
                }
            }
        }
        with open(self.status_file, 'w') as f:
            json.dump(initial_status, f, indent=2)