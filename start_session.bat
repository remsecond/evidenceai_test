@echo off
setlocal enabledelayedexpansion

:: Set base directory
set BASE_DIR=%~dp0

:: Create Python script for session initialization
echo Creating session initialization script...
python -c "
import json
from datetime import datetime
from pathlib import Path
import sys
import glob

def get_checkpoint_info():
    checkpoint_dir = Path('%BASE_DIR%') / 'output' / 'checkpoints'
    checkpoints = list(checkpoint_dir.glob('*.json')) if checkpoint_dir.exists() else []
    if checkpoints:
        latest = max(checkpoints, key=lambda p: p.stat().mtime)
        with open(latest) as f:
            data = json.load(f)
        return {
            'file': latest.name,
            'data': data
        }
    return {'file': 'None', 'data': {}}

def count_files(pattern):
    return len(glob.glob(str(Path('%BASE_DIR%') / pattern)))

def get_stage_status():
    stages = {
        'file_processing': [
            'File type validation',
            'Metadata extraction',
            'Message parsing',
            'Data integrity checks'
        ],
        'message_threading': [
            'Thread identification',
            'Parent-child relationships',
            'Thread metadata',
            'Validation checks'
        ],
        'analysis': [
            'Response time analysis',
            'Participant patterns',
            'Thread categorization',
            'Advanced pattern detection'
        ]
    }
    
    # Get completed stages from checkpoint
    checkpoint = get_checkpoint_info()
    completed = checkpoint['data'].get('completed_stages', [])
    
    status = {}
    for stage, tasks in stages.items():
        status[stage] = [
            (task, task.lower().replace(' ', '_') in completed)
            for task in tasks
        ]
    return status

def create_session_summary():
    # Get metrics
    checkpoint = get_checkpoint_info()
    status = get_stage_status()
    
    # Count files
    input_files = count_files('input/*.pdf')
    processed_files = count_files('processed/*.json')
    
    summary = f'''# EvidenceAI Development Session
## Project Status
Last checkpoint: {checkpoint['file']}
Current stage: {checkpoint['data'].get('current_stage', 'Initialization')}
## Directory Structure
```
evidenceai_test/
├── input/                  # Raw OFW PDFs ({input_files} files)
├── output/                 # Analysis outputs and checkpoints
└── src/                   
    ├── processors/        # File processing modules
    ├── parsers/           # Document parsing modules
    ├── threader/          # Message threading modules
    ├── analyzers/         # Analysis modules
    └── utils/             # Utility modules
```
## Pipeline Status
### File Processing Stage'''

    # Add status for each stage
    for stage, tasks in status.items():
        summary += f"\\n### {stage.replace('_', ' ').title()}"
        for task, completed in tasks:
            check = "[x]" if completed else "[ ]"
            summary += f"\\n- {check} {task}"

    # Add metrics
    metrics = checkpoint['data'].get('metrics', {})
    summary += f'''
## Current Status
Messages Processed: {metrics.get('messages_processed', 0)}
Threads Identified: {metrics.get('threads_identified', 0)}
Files Processed: {processed_files}/{input_files}
Success Rate: {(processed_files/input_files)*100:.1f}% if input_files else 'N/A'}

## Available Commands
```powershell
# Run pipeline test
python src/test_pipeline.py

# Check processing status
python src/report_checkpoints.py

# Process new files
python src/process_files.py

# Generate analysis
python src/analyze_data.py

# Run all tests
python -m unittest discover tests
```

## Quick Actions
1. Review last checkpoint:
   ```powershell
   python src/report_checkpoints.py
   ```

2. Process any new files:
   ```powershell
   python src/process_new.py
   ```

3. Generate analysis report:
   ```powershell
   python src/generate_report.py
   ```

## Development Guidelines
1. Review checkpoints before starting
2. Process files in batches when possible
3. Run tests after major changes
4. Update documentation for new features

## Next Steps
1. Check pending files in input/ directory
2. Review any failed processing attempts
3. Update analysis parameters if needed
4. Run validation on processed files

## Current Issues
{checkpoint['data'].get('current_issues', ['No active issues'])}

## Recent Changes
{checkpoint['data'].get('recent_changes', ['Initial setup'])}
'''
    
    # Save summary
    summary_path = Path('%BASE_DIR%') / 'SESSION_SUMMARY.md'
    with open(summary_path, 'w') as f:
        f.write(summary)
        
    print(f'Created session summary at {summary_path}')
    
create_session_summary()
" > create_summary.py

:: Run the session initialization
python create_summary.py

:: Create required directories if they don't exist
mkdir input 2>nul
mkdir output\checkpoints 2>nul
mkdir output\exports 2>nul
mkdir output\logs 2>nul
mkdir src\processors 2>nul
mkdir src\parsers 2>nul
mkdir src\threader 2>nul
mkdir src\analyzers 2>nul
mkdir src\utils 2>nul

echo Session initialized. Opening summary...
start "" "SESSION_SUMMARY.md"

:: Clean up temporary script
del create_summary.py

endlocal