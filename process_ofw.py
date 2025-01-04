"""Process OFW PDF and generate analysis."""
import PyPDF2
import json
from pathlib import Path
from datetime import datetime
import re

class OFWProcessor:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def process_pdf(self, pdf_name):
        """Process a single PDF file."""
        pdf_path = self.input_dir / pdf_name
        print(f"\nProcessing: {pdf_path}")
        
        try:
            # Read PDF
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                print(f"Pages found: {len(pdf.pages)}")
                
                # Extract text from all pages
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                # Split into messages
                messages = self._extract_messages(full_text)
                print(f"Messages found: {len(messages)}")
                
                # Save extracted messages
                output_file = self.output_dir / f"{pdf_path.stem}_messages.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'processed_at': datetime.now().isoformat(),
                        'source_file': pdf_name,
                        'message_count': len(messages),
                        'messages': messages
                    }, f, indent=2)
                
                print(f"Results saved to: {output_file}")
                return True
                
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return False
    
    def _extract_messages(self, text):
        """Extract individual messages from text."""
        messages = []
        
        # Split into message blocks
        blocks = re.split(r'Message \d+ of \d+', text)[1:]  # Skip header
        
        for block in blocks:
            try:
                message = self._parse_message(block.strip())
                if message:
                    messages.append(message)
            except Exception as e:
                print(f"Error parsing message block: {str(e)}")
        
        return messages
    
    def _parse_message(self, block):
        """Parse a single message block."""
        patterns = {
            'sent_time': r'Sent: (.*?)(?=\nFrom:|\Z)',
            'from': r'From: (.*?)(?=\nTo:|\Z)',
            'to': r'To: (.*?)(?=\nSubject:|\Z)',
            'subject': r'Subject: (.*?)(?=\nOn|\n\n|\Z)',
            'first_viewed': r'\(First Viewed: (.*?)\)'
        }
        
        message = {}
        
        # Extract fields using patterns
        for field, pattern in patterns.items():
            match = re.search(pattern, block)
            if match:
                message[field] = match.group(1).strip()
        
        # Extract first_viewed from recipient if present
        if 'to' in message and '(First Viewed:' in message['to']:
            to_parts = message['to'].split('(First Viewed:', 1)
            message['to'] = to_parts[0].strip()
            viewed_time = to_parts[1].rstrip(')').strip()
            message['first_viewed'] = viewed_time
        
        # Extract message content
        content_parts = block.split('\n\n', 1)
        if len(content_parts) > 1:
            message['content'] = content_parts[1].strip()
        else:
            message['content'] = ""
        
        return message if message else None

def main():
    """Main processing function."""
    base_dir = Path(__file__).parent
    processor = OFWProcessor(base_dir)
    
    # Process OFW PDF
    pdf_name = "OFW_Messages_Report_Dec.pdf"
    print(f"\nStarting OFW processing pipeline...")
    
    if processor.process_pdf(pdf_name):
        print("\nProcessing completed successfully!")
    else:
        print("\nProcessing failed!")

if __name__ == '__main__':
    main()