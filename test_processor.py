import os
from datetime import datetime
import PyPDF2
from pathlib import Path
import json

# Set explicit paths
BASE_DIR = Path(r"C:\Users\robmo\OneDrive\Documents\evidenceai_test")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

def test_file_access(filepath):
    """Simple test to verify we can access and read the PDF file."""
    try:
        # Basic file stats
        file_stats = os.stat(filepath)
        
        # Attempt to read PDF
        with open(filepath, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            page_count = len(pdf_reader.pages)
            # Read first page text as test
            first_page = pdf_reader.pages[0].extract_text()
        
        # Collect metadata
        metadata = {
            'filename': os.path.basename(filepath),
            'file_size': file_stats.st_size,
            'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'page_count': page_count,
            'first_page_preview': first_page[:500] if first_page else None  # First 500 chars
        }
        
        # Save metadata to JSON for inspection
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        with open(OUTPUT_DIR / 'test_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Successfully processed {metadata['filename']}")
        print(f"Page count: {metadata['page_count']}")
        print(f"File size: {metadata['file_size']} bytes")
        return True
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

if __name__ == '__main__':
    print(f"Using base directory: {BASE_DIR}")
    print(f"Looking for PDFs in: {INPUT_DIR}")
    
    # Ensure input directory exists
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir(parents=True)
        print(f"Created input directory at {INPUT_DIR.absolute()}")
        print("Please place your PDF file in this directory and run again")
        exit()
        
    # Look for PDF files
    pdf_files = list(INPUT_DIR.glob('*.pdf'))
    if not pdf_files:
        print("No PDF files found in input directory")
        print(f"Please place PDF files in: {INPUT_DIR}")
        exit()
        
    # Test first PDF found
    test_file = pdf_files[0]
    print(f"Testing file: {test_file}")
    success = test_file_access(test_file)
    print(f"\nTest completed {'successfully' if success else 'with errors'}")
    if success:
        print(f"Results saved to: {OUTPUT_DIR / 'test_metadata.json'}")