"""Create new development session."""

from datetime import datetime
import sys
from pathlib import Path
from utils.checkpoint_registry import CheckpointRegistry

def create_session():
    base_dir = Path(__file__).parent.parent
    registry = CheckpointRegistry(base_dir)
    status = registry.get_current_status()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_file = base_dir / f'SESSION_PROMPT_{timestamp}.md'
    
    with open(session_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# EvidenceAI Development Session - {datetime.now()}\n\n")
        
        # Previous Session Summary
        f.write("## Previous Session Summary\n")
        checkpoints = registry.get_checkpoint_history()
        if checkpoints:
            latest = checkpoints[-1]
            f.write(f"Last Stage: {latest['stage']}\n")
            f.write(f"Completion: {latest['timestamp']}\n")
            if 'status' in latest:
                f.write("\nResults:\n")
                for key, value in latest['status'].items():
                    f.write(f"- {key}: {value}\n")
        else:
            f.write("No previous session found\n")
        
        # Current Project Status
        f.write("\n## Current Project Status\n")
        f.write(f"Active Stage: {status['current_stage'] or 'Starting'}\n")
        f.write(f"Registry: {registry.registry_file}\n")
        f.write("\nMetrics:\n")
        f.write(f"- Messages Processed: {status['pipeline_status']['messages_processed']}\n")
        f.write(f"- Threads Created: {status['pipeline_status']['threads_identified']}\n")
        f.write(f"- Success Rate: {status['pipeline_status']['success_rate']}%\n")
        
        # Project Structure
        f.write("\n## Project Structure\n")
        f.write("```\n")
        f.write("evidenceai_test/\n")
        f.write("|-- input/                  # Raw OFW PDFs\n")
        f.write("|-- output/                 # Analysis outputs\n")
        f.write("|   |-- checkpoints/        # Processing checkpoints\n")
        f.write("|   |-- exports/           # AI tool exports\n")
        f.write("|   `-- logs/             # Processing logs\n")
        f.write("`-- src/                   # Source code\n")
        f.write("    |-- processors/        # Processing modules\n")
        f.write("    |-- parsers/           # Parser modules\n")
        f.write("    |-- threader/          # Threading modules\n")
        f.write("    |-- analyzers/         # Analysis modules\n")
        f.write("    `-- utils/             # Utility modules\n")
        f.write("```\n")
        
        # Current Issues
        f.write("\n## Current Issues\n")
        if status['pipeline_status']['last_issues']:
            for issue in status['pipeline_status']['last_issues']:
                f.write(f"- {issue}\n")
        else:
            f.write("No active issues\n")
        
        # Next Steps
        f.write("\n## Next Steps\n")
        f.write("### Immediate Actions\n")
        f.write("1. Fix Circular References\n")
        f.write("   - Update thread detection algorithm\n")
        f.write("   - Add cycle prevention\n")
        f.write("   - Implement validation checks\n\n")
        f.write("2. Thread Depth Control\n")
        f.write("   - Set maximum depth limit\n")
        f.write("   - Add depth tracking\n")
        f.write("   - Implement warning system\n\n")
        f.write("3. Participant Normalization\n")
        f.write("   - Create name standardization\n")
        f.write("   - Implement view time tracking\n")
        f.write("   - Add participant validation\n")
        
        # Session Commands
        f.write("\n## Available Commands\n")
        f.write("```powershell\n")
        f.write("# Option 1: Run Pipeline Test\n")
        f.write("python src/test_pipeline.py\n\n")
        f.write("# Option 2: Check Processing Status\n")
        f.write("python src/report_checkpoints.py\n\n")
        f.write("# Option 3: Run Specific Component Test\n")
        f.write("python src/test_component.py [parser|threader|validator]\n\n")
        f.write("# Option 4: Generate New Session\n")
        f.write("python src/create_session.py\n\n")
        f.write("# Option 5: View Pipeline Logs\n")
        f.write("python src/view_logs.py\n")
        f.write("```\n")
        
        # Development Guidelines
        f.write("\n## Development Guidelines\n")
        f.write("1. Work on one component at a time\n")
        f.write("2. Run tests after each major change\n")
        f.write("3. Update checkpoints regularly\n")
        f.write("4. Document new requirements\n")
        f.write("5. Validate outputs before proceeding\n")
        
        # Current Task Details
        f.write("\n## Current Task Details\n")
        f.write("### Circular Reference Fix\n")
        f.write("- Located in: src/threader/chain_builder.py\n")
        f.write("- Affected threads: 4\n")
        f.write("- Impact: Message linking accuracy\n")
        f.write("- Priority: High\n")
        f.write("\n### Thread Depth Issue\n")
        f.write("- Current max depth: 11\n")
        f.write("- Recommended max: 5\n")
        f.write("- Affected threads: Listed in validation report\n")
        f.write("- Priority: Medium\n")
        f.write("\n### Participant Tracking\n")
        f.write("- Current unique participants: 229\n")
        f.write("- Needs deduplication\n")
        f.write("- View time tracking needs normalization\n")
        f.write("- Priority: Medium\n")
    
    return session_file

if __name__ == '__main__':
    try:
        session_file = create_session()
        print(f"\nCreated new session file: {session_file}")
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        sys.exit(1)