"""Test EvidenceAI processing pipeline."""
import os
import json
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evidenceai")

def print_header():
    """Print colorful test header."""
    print("\033[95m==================================\033[0m")
    print("\033[95m   EvidenceAI Pipeline Tests      \033[0m")
    print("\033[95m==================================\033[0m")
    print(f"Python {os.sys.version.split()[0]}")

def print_config(input_dir, output_dir):
    """Print test configuration."""
    print("\033[96mTest Configuration:\033[0m")
    print("\033[96m------------------\033[0m")
    print(f"\033[97mInput Directory:\033[0m {input_dir}")
    print(f"\033[97mOutput Directory:\033[0m {output_dir}")

def run_tests(base_dir):
    """Run pipeline tests."""
    from processors.file_processor import FileProcessor
    
    try:
        # Initialize processor
        processor = FileProcessor(base_dir)
        
        # Process input files
        input_dir = base_dir / "input"
        output_dir = base_dir / "output"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'files_processed': 0,
            'errors': []
        }
        
        # Process PDF files
        for pdf_file in input_dir.glob('*.pdf'):
            try:
                logger.info(f"Processing {pdf_file.name}")
                metadata = processor.process_pdf(pdf_file)
                results['files_processed'] += 1
                
                # Extract text
                text = processor.extract_text(pdf_file)
                
                # Save extracted text
                text_file = output_dir / f"{pdf_file.stem}_text.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
            except Exception as e:
                error = {
                    'file': pdf_file.name,
                    'error': str(e)
                }
                results['errors'].append(error)
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
        
        # Save test results
        results_file = output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print("\033[92m✔ Test run completed successfully!\033[0m")
        return True
        
    except Exception as e:
        print(f"\033[91m✘ Test run failed: {str(e)}\033[0m")
        return False

def main():
    """Run main test sequence."""
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Ensure directories exist
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Print header
    print_header()
    print_config(input_dir, output_dir)
    
    # Run tests
    print("\033[95mRunning tests...\033[0m")
    print("\033[90m-----------------\033[0m")
    
    success = run_tests(base_dir)
    
    # Print results
    print("\033[94mTest Results:\033[0m")
    print("\033[94m-------------\033[0m")
    if success:
        print("\033[92m✓ Results saved to output directory\033[0m")
    else:
        print("\033[91m✘ Test run failed! Check the error messages above.\033[0m")
    
    print("\033[93mPress any key to exit...\033[0m")
    input()

if __name__ == '__main__':
    main()