"""Test specific pipeline components."""

import argparse
from pathlib import Path
from parsers.pdf_parser import OFWParser
from threader.chain_builder import MessageThreader
from validators.thread_validator import ThreadValidator
from utils.checkpoint_registry import CheckpointRegistry

def test_parser(input_file: str):
    """Test PDF parser component."""
    print("\nTesting PDF Parser...")
    base_dir = Path(__file__).parent.parent
    parser = OFWParser(base_dir / "input")
    results = parser.parse_pdf(input_file)
    
    print(f"Status: {results['status']}")
    if results['status'] == 'success':
        print(f"Messages Found: {len(results['messages'])}")
        print("\nSample Message:")
        msg = results['messages'][0]
        for key, value in msg.items():
            if key == 'content':
                print(f"{key}: {value[:100]}...")
            else:
                print(f"{key}: {value}")

def test_threader(input_file: str):
    """Test message threading component."""
    print("\nTesting Message Threader...")
    base_dir = Path(__file__).parent.parent
    parser = OFWParser(base_dir / "input")
    results = parser.parse_pdf(input_file)
    
    if results['status'] == 'success':
        threader = MessageThreader()
        threads = threader.process_messages(results['messages'])
        metadata = threader.get_thread_metadata()
        stats = threader.get_thread_statistics()
        
        print(f"Threads Created: {len(threads)}")
        print("\nThread Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")

def test_validator(input_file: str):
    """Test thread validation component."""
    print("\nTesting Thread Validator...")
    base_dir = Path(__file__).parent.parent
    parser = OFWParser(base_dir / "input")
    results = parser.parse_pdf(input_file)
    
    if results['status'] == 'success':
        threader = MessageThreader()
        threads = threader.process_messages(results['messages'])
        metadata = threader.get_thread_metadata()
        
        validator = ThreadValidator()
        validation = validator.validate_threading_results(threads, metadata)
        
        print(f"Validation Status: {validation['valid']}")
        print(f"Errors: {len(validation['errors'])}")
        print(f"Warnings: {len(validation['warnings'])}")
        
        if validation['errors']:
            print("\nErrors Found:")
            for error in validation['errors']:
                print(f"- {error}")

def main():
    parser = argparse.ArgumentParser(description='Test specific pipeline components')
    parser.add_argument('component', choices=['parser', 'threader', 'validator'],
                      help='Component to test')
    parser.add_argument('--file', default='OFW_Messages_Report_Dec.pdf',
                      help='Input file to use (default: OFW_Messages_Report_Dec.pdf)')
    
    args = parser.parse_args()
    
    if args.component == 'parser':
        test_parser(args.file)
    elif args.component == 'threader':
        test_threader(args.file)
    elif args.component == 'validator':
        test_validator(args.file)

if __name__ == '__main__':
    main()