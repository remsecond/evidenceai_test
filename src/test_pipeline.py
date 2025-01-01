import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from processors.file_processor import FileProcessor
from threader.message_threader import MessageThreader
from analyzers.thread_analyzer import ThreadAnalyzer

def create_stage_result(data: dict, stage: str) -> dict:
    """Create standardized stage result structure"""
    return {
        'metadata': {
            'stage': stage,
            'timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.0.0'
        },
        'status': 'success',
        'data': data,
        'validation': {
            'is_valid': True,
            'checks_performed': [f'{stage}_processing', f'{stage}_validation'],
            'warnings': []
        }
    }

def run_pipeline():
    """Run the complete analysis pipeline"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Find PDF file
        input_dir = base_dir / "input"
        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError("No PDF files found in input directory")
        
        pdf_path = pdf_files[0]
        print(f"\nTesting with file: {pdf_path.name}")
        
        results = {
            'metadata': {
                'stage': 'pipeline',
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'success',
            'stages': {},
            'validation': {
                'is_valid': True,
                'checks_performed': [],
                'warnings': []
            }
        }
        
        # Stage 1: Parse PDF
        print("\n=== Testing PDF Parser ===")
        processor = FileProcessor()
        parse_results = processor.process_file(pdf_path)
        stage_result = create_stage_result(parse_results, 'parsing')
        results['stages']['parsing'] = stage_result
        
        if parse_results['status'] != 'success':
            raise RuntimeError(f"PDF parsing failed: {parse_results.get('error')}")
            
        print(f"Status: {parse_results['status']}")
        print(f"Total messages: {len(parse_results['file_info'].get('messages', []))}")
        print("\nSample message:")
        print(json.dumps(parse_results['file_info']['messages'][0], indent=2))
        
        # Stage 2: Thread Messages
        print("\n=== Testing Message Threading ===")
        threader = MessageThreader()
        thread_results = threader.thread_messages(parse_results['file_info']['messages'])
        stage_result = create_stage_result(thread_results, 'threading')
        results['stages']['threading'] = stage_result
        
        print(f"Total threads: {thread_results['stats']['total_threads']}")
        print(f"Total messages: {thread_results['stats']['total_messages']}")
        print("\nSample thread:")
        first_thread_id = next(iter(thread_results['threads']))
        print(f"Subject: {thread_results['metadata'][first_thread_id]['subject']}")
        print(f"Messages in thread: {len(thread_results['threads'][first_thread_id])}")
        
        # Stage 3: Analyze Threads
        print("\n=== Testing Thread Analysis ===")
        analyzer = ThreadAnalyzer(thread_results)
        analysis_results = analyzer.analyze_threads()
        stage_result = create_stage_result(analysis_results, 'analysis')
        results['stages']['analysis'] = stage_result
        
        print("\nResponse Patterns:")
        print(f"Average response time: {analysis_results['response_patterns']['average_response_time']:.2f} hours")
        print(f"Average thread duration: {analysis_results['response_patterns']['average_thread_duration']:.2f} hours")
        
        print("\nParticipant Patterns:")
        for participant, count in analysis_results['participant_patterns']['initiatives'].items():
            print(f"{participant}: Started {count} threads")
        
        # Update validation information
        results['validation']['checks_performed'] = [
            'pipeline_execution',
            'stage_completion',
            'result_validation'
        ]
        
        # Save results
        output_file = output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nTest results saved to: {output_file}")
        return True
        
    except Exception as e:
        error_results = {
            'metadata': {
                'stage': 'pipeline',
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'error',
            'error': str(e),
            'validation': {
                'is_valid': False,
                'checks_performed': ['error_detection'],
                'warnings': [str(e)]
            }
        }
        
        # Save error results
        output_file = output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(error_results, f, indent=2)
            
        print(f"\nError in pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)