import argparse
import logging
from pathlib import Path
import PyPDF2
import re
from datetime import datetime

def process_document(file_path, output_dir):
    try:
        with open(file_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n\n"
            
            # Process message blocks
            messages = re.split(r'Message \d+ of \d+', full_text)[1:]
            
            # Save structured data
            output_file = Path(output_dir) / f"{Path(file_path).stem}_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'file': str(file_path),
                    'processed_at': datetime.now().isoformat(),
                    'message_count': len(messages),
                    'messages': messages
                }, f, indent=2)
                
            return True
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=int, required=True)
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent.parent
    input_dir = base_dir / 'input'
    output_dir = base_dir / 'output' / 'processed'
    output_dir.mkdir(exist_ok=True)
    
    if args.mode == 1:  # Process new
        for pdf in input_dir.glob('*.pdf'):
            process_document(pdf, output_dir)
    elif args.mode == 2:  # Update existing
        # Implement update logic
        pass
    elif args.mode == 3:  # View status
        # Show processing status
        pass

if __name__ == '__main__':
    main()