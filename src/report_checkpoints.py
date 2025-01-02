"""Report current checkpoint status."""

from pathlib import Path
from utils.checkpoint_registry import CheckpointRegistry

def main():
    base_dir = Path(__file__).parent.parent
    registry = CheckpointRegistry(base_dir)
    status = registry.get_current_status()
    
    print("\nEvidenceAI Pipeline Status")
    print("-" * 50)
    print(f"Last Update: {status['last_update']}")
    print(f"Current Stage: {status['current_stage']}")
    print("\nProcessing Statistics:")
    print(f"Messages Processed: {status['pipeline_status']['messages_processed']}")
    print(f"Threads Identified: {status['pipeline_status']['threads_identified']}")
    print(f"Success Rate: {status['pipeline_status']['success_rate']}%")
    
    if status['pipeline_status']['last_issues']:
        print("\nCurrent Issues:")
        for issue in status['pipeline_status']['last_issues']:
            print(f"- {issue}")

if __name__ == '__main__':
    main()