"""PDF parsing module."""

from pathlib import Path
import PyPDF2
import re
from datetime import datetime
from typing import Dict, List

class OFWParser:
    """Parser for Our Family Wizard PDF exports."""
    
    def __init__(self, input_path: Path):
        self.input_path = Path(input_path)
    
    def parse_pdf(self, filename: str) -> Dict:
        """Parse PDF and extract messages."""
        filepath = self.input_path / filename
        
        try:
            with open(filepath, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                metadata = self._extract_metadata(pdf)
                messages = self._extract_messages(pdf)
                
                return {
                    'status': 'success',
                    'metadata': metadata,
                    'messages': messages,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_metadata(self, pdf: PyPDF2.PdfReader) -> Dict:
        """Extract PDF and OFW metadata."""
        first_page = pdf.pages[0].extract_text()
        metadata = {
            'pdf_info': {
                'pages': len(pdf.pages),
                'created': datetime.now().isoformat()
            }
        }
        
        patterns = {
            'generated_date': r'Generated:\s*([^\n]+)',
            'message_count': r'Number of messages:\s*(\d+)',
            'timezone': r'Timezone:\s*([^\n]+)',
            'participants': r'Parents:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            if match := re.search(pattern, first_page):
                metadata[key] = match.group(1).strip()
        
        return metadata
    
    def _extract_messages(self, pdf: PyPDF2.PdfReader) -> List[Dict]:
        """Extract individual messages from PDF."""
        messages = []
        full_text = ""
        
        for page in pdf.pages:
            full_text += page.extract_text() + "\n\n"
        
        message_blocks = re.split(r'Message \d+ of \d+', full_text)[1:]
        
        for i, block in enumerate(message_blocks, 1):
            if block and (message := self._parse_message_block(block.strip(), i)):
                messages.append(message)
        
        return messages
    
    def _parse_message_block(self, block: str, index: int) -> Dict:
        """Parse a single message block."""
        patterns = {
            'sent': r'Sent:\s*(.*?)(?=\nFrom:|$)',
            'from': r'From:\s*(.*?)(?=\nTo:|$)',
            'to': r'To:\s*(.*?)(?=\nSubject:|$)',
            'subject': r'Subject:\s*(.*?)(?=\nOn|$)',
            'viewed': r'\(First Viewed:\s*(.*?)\)'
        }
        
        message = {'index': index}
        
        try:
            # Extract header components
            for key, pattern in patterns.items():
                if match := re.search(pattern, block):
                    message[key] = match.group(1).strip()
            
            # Extract content - everything after headers
            parts = block.split('\n\n', 1)
            message['content'] = parts[1].strip() if len(parts) > 1 else ""
            
            # Convert to standard format
            if sent_time := message.get('sent'):
                try:
                    dt = datetime.strptime(sent_time, '%m/%d/%Y at %I:%M %p')
                    message['timestamp'] = dt.isoformat()
                except ValueError:
                    message['timestamp'] = None
            
            if 'from' not in message or 'timestamp' not in message:
                return None
                
            return message
            
        except Exception as e:
            print(f"Error parsing message {index}: {str(e)}")
            return None