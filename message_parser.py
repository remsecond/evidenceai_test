import PyPDF2
from pathlib import Path
import json
import re
from datetime import datetime

class OFWMessageParser:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.messages = []
        
    def parse_messages(self):
        """Extract all messages from the PDF."""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                # Split into messages using the "Message X of Y" pattern
                message_blocks = re.split(r'Message \d+ of \d+', full_text)[1:]  # Skip header
                message_count = len(message_blocks)
                print(f"Found {message_count} message blocks")
                
                for i, block in enumerate(message_blocks, 1):
                    try:
                        message = self._parse_message_block(block)
                        if message:
                            self.messages.append(message)
                            if i % 50 == 0:  # Progress update every 50 messages
                                print(f"Processed {i} of {message_count} messages")
                    except Exception as e:
                        print(f"Error parsing message {i}: {str(e)}")
                
                return self.messages
                
    def _parse_message_block(self, block):
        """Parse a single message block into structured data."""
        # Regular expressions for parsing
        sent_pattern = r'Sent: (.*?)(?=\nFrom:|\Z)'
        from_pattern = r'From: (.*?)(?=\nTo:|\Z)'
        to_pattern = r'To: (.*?)(?=\nSubject:|\Z)'
        subject_pattern = r'Subject: (.*?)(?=\nOn|\n\n|\Z)'
        viewed_pattern = r'\(First Viewed: (.*?)\)'
        
        try:
            # Extract components
            sent = re.search(sent_pattern, block)
            from_user = re.search(from_pattern, block)
            to_user = re.search(to_pattern, block)
            subject = re.search(subject_pattern, block)
            viewed = re.search(viewed_pattern, block)
            
            # Get message content - everything after the header info
            content = block.split('\n\n', 1)[-1].strip()
            
            # Build message object
            message = {
                'sent_time': sent.group(1).strip() if sent else None,
                'from': from_user.group(1).strip() if from_user else None,
                'to': to_user.group(1).strip() if to_user else None,
                'subject': subject.group(1).strip() if subject else None,
                'first_viewed': viewed.group(1).strip() if viewed else None,
                'content': content
            }
            
            return message
            
        except Exception as e:
            print(f"Error parsing message block: {str(e)}")
            return None
    
    def save_messages(self, output_path):
        """Save parsed messages to JSON file."""
        output_file = Path(output_path) / 'parsed_messages.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source_file': self.pdf_path.name,
                    'message_count': len(self.messages),
                    'parsed_at': datetime.now().isoformat()
                },
                'messages': self.messages
            }, f, indent=2)
        print(f"Saved {len(self.messages)} messages to {output_file}")

def main():
    # Paths
    base_dir = Path(r"C:\Users\robmo\OneDrive\Documents\evidenceai_test")
    pdf_path = base_dir / "input" / "OFW_Messages_Report_Dec.pdf"
    output_dir = base_dir / "output"
    
    # Parse messages
    parser = OFWMessageParser(pdf_path)
    messages = parser.parse_messages()
    parser.save_messages(output_dir)
    
    # Print sample of first message
    if messages:
        print("\nFirst message sample:")
        sample = messages[0]
        for key, value in sample.items():
            if key == 'content':
                print(f"{key}: {value[:100]}...")  # First 100 chars of content
            else:
                print(f"{key}: {value}")

if __name__ == '__main__':
    main()