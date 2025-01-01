import json
from pathlib import Path
from datetime import datetime
import sys

def find_last_checkpoint():
    """Find the most recent checkpoint file"""
    base_dir = Path(__file__).parent.parent
    checkpoint_dir = base_dir / "output" / "checkpoints"
    
    if not checkpoint_dir.exists():
        return None, None
        
    checkpoints = list(checkpoint_dir.glob("*_*.json"))
    if not checkpoints:
        return None, None
        
    latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest) as f:
            data = json.load(f)
    except Exception:
        data = {}
    
    return latest, data

def get_analysis_stats():
    """Get latest analysis statistics"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    
    results_files = list(output_dir.glob("test_results_*.json"))
    if not results_files:
        return None
        
    latest = max(results_files, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest) as f:
            data = json.load(f)
            return {
                'message_count': data.get('results', {}).get('parsing', {}).get('file_info', {}).get('message_count', 0),
                'thread_count': data.get('results', {}).get('threading', {}).get('stats', {}).get('total_threads', 0)
            }
    except:
        return None

def generate_session_prompt():
    """Generate a new session prompt with current status"""
    base_dir = Path(__file__).parent.parent
    template_path = base_dir / "NEW_SESSION_PROMPT.md"
    
    if not template_path.exists():
        print("Template not found!")
        return
        
    # Get latest checkpoint and analysis stats
    last_checkpoint, checkpoint_data = find_last_checkpoint()
    stats = get_analysis_stats()
    
    # Read template
    with open(template_path) as f:
        template = f.read()
        
    # Update placeholder values
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    prompt = template.replace(
        "{LAST_CHECKPOINT_FILE}", 
        str(last_checkpoint.name) if last_checkpoint else "None"
    )
    
    # Determine current stage
    if last_checkpoint:
        stage = last_checkpoint.name.split('_')[0]
    else:
        stage = "Not started"
    
    prompt = prompt.replace("{CURRENT_STAGE}", stage)
    
    # Add analysis stats
    if stats:
        prompt = prompt.replace("{MESSAGE_COUNT}", str(stats['message_count']))
        prompt = prompt.replace("{THREAD_COUNT}", str(stats['thread_count']))
    else:
        prompt = prompt.replace("{MESSAGE_COUNT}", "0")
        prompt = prompt.replace("{THREAD_COUNT}", "0")
    
    # Create output directory if needed
    output_dir = base_dir
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Save as new prompt
    output_path = output_dir / f"SESSION_PROMPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_path, 'w') as f:
        f.write(f"# EvidenceAI Development Session - {current_time}\n\n")
        f.write(prompt)
    
    print(f"\nNew session prompt generated: {output_path}")
    
    # Show key information
    print("\nSession Status:")
    print(f"Last Checkpoint: {last_checkpoint.name if last_checkpoint else 'None'}")
    print(f"Current Stage: {stage}")
    print(f"Time: {current_time}")
    
if __name__ == "__main__":
    generate_session_prompt()