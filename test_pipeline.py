"""
End-to-end test of the EvidenceAI threading pipeline with detailed output.
"""

from pathlib import Path
from datetime import datetime
import json
import sys
from src.integration import ThreadingOrchestrator

def print_section(title, char='='):
    """Print a section header"""
    print(f"\n{char * 80}")
    print(f"{title}")
    print(f"{char * 80}\n")

def print_dict(data, indent=0):
    """Pretty print dictionary with proper indentation"""
    for key, value in data.items():
        prefix = "  " * indent
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{key}:")
            for item in value[:5]:  # Show first 5 items
                print(f"{prefix}  - {item}")
            if len(value) > 5:
                print(f"{prefix}  ... ({len(value) - 5} more items)")
        else:
            print(f"{prefix}{key}: {value}")

def analyze_exports(output_dir):
    """Analyze export files"""
    exports_dir = output_dir / 'exports'
    if not exports_dir.exists():
        return None
        
    export_analysis = {}
    for export_file in exports_dir.glob('*.json'):
        with open(export_file) as f:
            data = json.load(f)
            export_analysis[export_file.stem] = {
                'size': export_file.stat().st_size,
                'format_version': data.get('format_version'),
                'timestamp': data.get('timestamp'),
                'type': data.get('tool')
            }
    return export_analysis

def analyze_validation(output_dir, filename):
    """Analyze validation results"""
    results_dir = output_dir / filename.replace('.pdf', '')
    validation_file = results_dir / 'validation.json'
    
    if not validation_file.exists():
        return None
        
    with open(validation_file) as f:
        return json.load(f)

def analyze_metadata(output_dir, filename):
    """Analyze enhanced metadata"""
    results_dir = output_dir / filename.replace('.pdf', '')
    metadata_file = results_dir / 'metadata.json'
    
    if not metadata_file.exists():
        return None
        
    with open(metadata_file) as f:
        return json.load(f)

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    filename = "OFW_Messages_Report_Dec.pdf"
    
    print_section("EvidenceAI Pipeline Test")
    print(f"Test Start Time: {datetime.now()}")
    print(f"Input Directory: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"Target File: {filename}")
    
    # Initialize orchestrator
    print_section("Initializing Pipeline", '-')
    orchestrator = ThreadingOrchestrator(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    # Process file
    print_section("Starting Processing", '-')
    start_time = datetime.now()
    
    results = orchestrator.process_file(
        filename,
        checkpoint=True,
        export_formats=['notebooklm', 'chatgpt', 'gemini']
    )
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Print detailed results
    print_section("Processing Results")
    print(f"Overall Status: {results['status']}")
    print(f"Total Processing Time: {processing_time:.2f} seconds")
    
    print_section("Stage Details", '-')
    for stage, info in results.get('stages', {}).items():
        print(f"\n{stage.upper()}:")
        print_dict(info, indent=1)
    
    print_section("Statistics", '-')
    stats = results.get('statistics', {})
    print("Message Statistics:")
    print(f"  Total Messages: {stats.get('messages', 'N/A')}")
    print(f"  Total Threads: {stats.get('threads', 'N/A')}")
    
    if thread_stats := stats.get('thread_stats'):
        print("\nDetailed Thread Statistics:")
        print_dict(thread_stats, indent=1)
    
    # Analyze exports
    print_section("Export Analysis", '-')
    if export_analysis := analyze_exports(output_dir):
        print_dict(export_analysis)
    else:
        print("No exports found")
    
    # Analyze validation
    print_section("Validation Results", '-')
    if validation_results := analyze_validation(output_dir, filename):
        print("Validation Status:")
        print(f"  Valid: {validation_results.get('valid', False)}")
        print(f"  Error Count: {len(validation_results.get('errors', []))}")
        print(f"  Warning Count: {len(validation_results.get('warnings', []))}")
        
        if validation_results.get('stats'):
            print("\nValidation Statistics:")
            print_dict(validation_results['stats'], indent=1)
            
        if validation_results.get('errors'):
            print("\nValidation Errors:")
            for error in validation_results['errors']:
                print(f"  - {error}")
    else:
        print("No validation results found")
    
    # Analyze metadata
    print_section("Metadata Analysis", '-')
    if metadata := analyze_metadata(output_dir, filename):
        thread_count = len(metadata)
        print(f"Total Threads: {thread_count}")
        
        participant_set = set()
        total_messages = 0
        max_depth = 0
        
        for thread_data in metadata.values():
            if isinstance(thread_data, dict):
                total_messages += thread_data.get('message_count', 0)
                max_depth = max(max_depth, thread_data.get('depth', 0))
                participant_set.update(thread_data.get('participants', []))
        
        print("\nMetadata Summary:")
        print(f"  Total Messages: {total_messages}")
        print(f"  Maximum Thread Depth: {max_depth}")
        print(f"  Unique Participants: {len(participant_set)}")
        if participant_set:
            print("\nParticipants:")
            for participant in sorted(participant_set):
                print(f"  - {participant}")
    else:
        print("No metadata found")
    
    print_section("Test Complete")
    print(f"End Time: {datetime.now()}")
    print(f"Total Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        raise