from pathlib import Path
import json
import os
from datetime import datetime
from enum import Enum, auto

class DevelopmentStage(Enum):
    """Tracks both development and execution stages"""
    SETUP_COMPLETE = auto()
    PDF_PARSER_IMPLEMENTED = auto()
    THREADING_IMPLEMENTED = auto()
    RELATIONSHIPS_IMPLEMENTED = auto()
    TOPICS_IMPLEMENTED = auto()
    TESTS_IMPLEMENTED = auto()
    ANALYSIS_COMPLETE = auto()

class WorkflowManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.checkpoint_dir = self.base_dir / "output" / "checkpoints"
        self.dev_checkpoint_dir = self.base_dir / "dev_checkpoints"
        self.status_file = self.base_dir / "src" / "project_status.json"
        self.session_file = self.base_dir / "output" / "current_session.txt"
        
        # Create directories
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.dev_checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize status
        self.load_status()

    def load_status(self):
        """Load or create project status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
            else:
                self.create_initial_status()
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
                
            # Update implementation status
            self.implementation_status = self._get_implementation_status()
        except Exception as e:
            print(f"Error loading status: {str(e)}")
            self.status = {}
            self.implementation_status = {'modules': {}}
    
    def _get_implementation_status(self):
        """Get current implementation status"""
        return {
            'modules': {
                module: details.get('status', 'pending')
                for module, details in self.status.get('project_overview', {}).get('modules', {}).items()
            }
        }
        
    def create_initial_status(self):
        """Create initial project status"""
        initial_status = {
            "project_overview": {
                "name": "EvidenceAI",
                "current_phase": "Setup",
                "modules": {
                    "parsing": {
                        "status": "complete",
                        "current_focus": False,
                        "progress": ["Initial setup complete", "PDF parser implemented", "Basic tests created"]
                    },
                    "threading": {
                        "status": "in_progress",
                        "current_focus": True,
                        "progress": ["Basic framework created"],
                        "pending": ["Implement message linking", "Add thread detection", "Create tests"]
                    },
                    "relationship_analysis": {
                        "status": "pending",
                        "dependencies": ["threading"]
                    },
                    "topic_detection": {
                        "status": "pending",
                        "dependencies": ["threading"]
                    },
                    "deliverable_generation": {
                        "status": "pending",
                        "dependencies": ["relationship_analysis", "topic_detection"]
                    }
                }
            }
        }
        
        # Create src directory if it doesn't exist
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.status_file, 'w') as f:
            json.dump(initial_status, f, indent=2)
    
    def print_implementation_status(self):
        """Print current implementation status"""
        print("\nModule Implementation Status:")
        for module, status in self.implementation_status.get('modules', {}).items():
            symbol = "✓" if status == "complete" else "-"
            print(f"{symbol} {module}: {status}")
            
    def start_from_last_or_fresh(self):
        """Check for previous checkpoints and get user preference"""
        # Find valid checkpoints (excluding ERROR states)
        checkpoints = [
            cp for cp in self.checkpoint_dir.glob("checkpoint_*.json")
            if not cp.name.startswith("checkpoint_ERROR")
        ]
        
        if not checkpoints:
            print("No previous successful checkpoints found. Starting fresh.")
            return None
            
        try:
            latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
            with open(latest_checkpoint, 'r') as f:
                checkpoint_data = json.load(f)
                
            print(f"\nFound previous successful checkpoint:")
            print(f"Stage: {checkpoint_data.get('stage', 'unknown')}")
            print(f"Time: {checkpoint_data.get('timestamp', 'unknown')}")
            print(f"Last Status: {checkpoint_data.get('data', {}).get('status', 'unknown')}")
            
            while True:
                choice = input("\nWould you like to:\n1. Continue from last checkpoint\n2. Start fresh\nChoice (1-2): ")
                if choice == "1":
                    return checkpoint_data.get('stage')
                elif choice == "2":
                    return None
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        except Exception as e:
            print(f"Error reading checkpoint: {str(e)}")
            print("Starting fresh for safety.")
            return None
            
    def save_checkpoint(self, stage, data):
        """Save a checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{stage}_{timestamp}.json"
        
        save_data = {
            "stage": stage,
            "timestamp": timestamp,
            "data": data,
            "implementation_status": self.implementation_status
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
            
        print(f"\nCheckpoint saved: {checkpoint_file.name}")
        
    def save_session_info(self, info):
        """Save session information for Claude to read"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            f.write(f"=== EvidenceAI Session Info ===\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write("Current Development Status:\n")
            f.write(f"- Stage: {info.get('stage', 'Unknown')}\n")
            f.write(f"- Focus: {info.get('focus', 'Unknown')}\n")
            f.write("\nImplementation Status:\n")
            for module, status in self.implementation_status.get('modules', {}).items():
                f.write(f"- {module}: {status}\n")
            f.write("\nProgress:\n")
            for item in info.get('progress', []):
                f.write(f"* {item}\n")
            f.write("\nPending:\n")
            for item in info.get('pending', []):
                f.write(f"- {item}\n")
            f.write("\nRecent Checkpoints:\n")
            checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.json"))
            for cp in sorted(checkpoints, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
                f.write(f"- {cp.name}\n")
                
        print(f"\nSession info saved to: {self.session_file}")

    def start_session(self):
        """Start a new development session"""
        try:
            # Get current focus
            current_module = None
            module_details = {}
            for module, details in self.status.get('project_overview', {}).get('modules', {}).items():
                if details.get('current_focus'):
                    current_module = module
                    module_details = details
                    break
                    
            # Save session info
            session_info = {
                'stage': self.status.get('project_overview', {}).get('current_phase', 'Unknown'),
                'focus': current_module,
                'progress': module_details.get('progress', []),
                'pending': module_details.get('pending', [])
            }
            self.save_session_info(session_info)
            
            return session_info
            
        except Exception as e:
            print(f"\nError starting session: {str(e)}")
            return {}

# Make sure these are exposed at the module level
__all__ = ['WorkflowManager', 'DevelopmentStage']

if __name__ == "__main__":
    workflow = WorkflowManager()
    session_info = workflow.start_session()
    workflow.print_implementation_status()