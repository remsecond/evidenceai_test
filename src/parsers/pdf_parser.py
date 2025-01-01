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
                'created': datetime.now().isoformat()  # Placeholder for actual PDF creation date
            }
        }
        
        # Extract OFW-specific metadata
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
        
        # Combine all pages
        for page in pdf.pages:
            full_text += page.extract_text() + "\n\n"
        
        # Split into message blocks
        message_blocks = re.split(r'Message \d+ of \d+', full_text)[1:]  # Skip header
        
        for i, block in enumerate(message_blocks, 1):
            if message := self._parse_message_block(block.strip(), i):
                messages.append(message)
        
        return messages
    
    def _parse_message_block(self, block: str, index: int) -> Dict:
        """Parse a single message block."""
        try:
            # Extract components using regex
            sent_match = re.search(r'Sent: (.*?)(?=\nFrom:|$)', block)
            from_match = re.search(r'From: (.*?)(?=\nTo:|$)', block)
            to_match = re.search(r'To: (.*?)(?=\nSubject:|$)', block)
            subject_match = re.search(r'Subject: (.*?)(?=\nOn|$)', block)
            viewed_match = re.search(r'\(First Viewed: (.*?)\)', block)
            
            # Split content from headers
            content_parts = block.split('\n\n', 1)
            content = content_parts[1] if len(content_parts) > 1 else ""
            
            message = {
                'index': index,
                'timestamp': self._parse_timestamp(sent_match.group(1) if sent_match else None),
                'from': from_match.group(1).strip() if from_match else None,
                'to': to_match.group(1).strip() if to_match else None,
                'subject': subject_match.group(1).strip() if subject_match else None,
                'content': content.strip(),
                'first_viewed': viewed_match.group(1).strip() if viewed_match else None
            }
            
            return message
            
        except Exception as e:
            print(f"Error parsing message {index}: {str(e)}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> str:
        """Parse OFW timestamp to ISO format."""
        if not timestamp_str:
            return None
            
        try:
            dt = datetime.strptime(timestamp_str.strip(), '%m/%d/%Y at %I:%M %p')
            return dt.isoformat()
        except ValueError:
            return None