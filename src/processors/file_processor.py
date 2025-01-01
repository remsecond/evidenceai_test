import os
import mimetypes
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import PyPDF2
import json
import re
import sys

class FileProcessor:
    """Handles initial file processing and validation"""
    
    SUPPORTED_TYPES = {
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel'
    }

    OFW_MARKERS = [
        "OurFamilyWizard",
        "Message Report",
        "Number of messages:",
        "Timezone:"
    ]
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parents[2]
    
    def process_file(self, file_path: Path) -> Dict:
        """Process uploaded file and extract initial metadata"""
        try:
            # Verify file exists and is readable
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get basic file information
            file_info = self._get_file_info(file_path)
            
            # Validate file type
            mime_type = self._validate_file_type(file_path)
            file_info['mime_type'] = mime_type
            
            # Extract messages if it's an OFW PDF
            if mime_type == 'application/pdf':
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    if self._check_ofw_format(pdf):
                        messages = self._extract_messages(pdf)
                        file_info['messages'] = messages
                        file_info['message_count'] = len(messages)
                    else:
                        file_info['messages'] = []
                        file_info['message_count'] = 0
            
            return {
                'status': 'success',
                'file_info': file_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_file_info(self, file_path: Path) -> Dict:
        """Get basic file information"""
        stats = file_path.stat()
        return {
            'filename': file_path.name,
            'file_size': stats.st_size,
            'created_time': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'file_extension': file_path.suffix.lower()
        }
    
    def _validate_file_type(self, file_path: Path) -> str:
        """Validate file type and return mime type"""
        extension = file_path.suffix.lower()
        
        if extension not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {extension}")
            
        return self.SUPPORTED_TYPES[extension]
    
    def _check_ofw_format(self, pdf: PyPDF2.PdfReader) -> bool:
        """Check if PDF is an OFW export"""
        try:
            first_page = pdf.pages[0].extract_text()
            return all(marker in first_page for marker in self.OFW_MARKERS)
        except:
            return False
    
    def _extract_messages(self, pdf: PyPDF2.PdfReader) -> List[Dict]:
        """Extract messages from OFW PDF"""
        messages = []
        full_text = ""
        
        # Combine all pages
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Split into message blocks
        blocks = re.split(r'Message \d+ of \d+', full_text)[1:]  # Skip header
        
        for i, block in enumerate(blocks, 1):
            try:
                message = self._parse_message_block(block.strip(), i)
                if message:
                    messages.append(message)
            except Exception as e:
                print(f"Error parsing message {i}: {str(e)}")
        
        return messages
    
    def _parse_message_block(self, block: str, index: int) -> Optional[Dict]:
        """Parse a message block into structured data"""
        patterns = {
            'sent_time': r'Sent: (.*?)(?=\nFrom:|\Z)',
            'from': r'From: (.*?)(?=\nTo:|\Z)',
            'to': r'To: (.*?)(?=\nSubject:|\Z)',
            'subject': r'Subject: (.*?)(?=\nOn|\n\n|\Z)',
            'first_viewed': r'\(First Viewed: (.*?)\)'
        }
        
        message = {}
        
        # Extract header fields
        for field, pattern in patterns.items():
            match = re.search(pattern, block)
            if match:
                message[field] = match.group(1).strip()
        
        # Clean up recipient field and extract viewed time
        if 'to' in message and '(First Viewed:' in message['to']:
            to_parts = message['to'].split('(First Viewed:', 1)
            message['to'] = to_parts[0].strip()
            viewed_time = to_parts[1].rstrip(')').strip()
            message['first_viewed'] = viewed_time
        
        # Extract content
        header_end = block.find('\n\n')
        if header_end != -1:
            message['content'] = block[header_end:].strip()
        else:
            message['content'] = ''
        
        # Add timestamps
        if 'sent_time' in message:
            try:
                message['timestamp'] = datetime.strptime(
                    message['sent_time'],
                    '%m/%d/%Y at %I:%M %p'
                ).isoformat()
            except:
                message['timestamp'] = None
        
        if message.get('first_viewed'):
            try:
                message['viewed_timestamp'] = datetime.strptime(
                    message['first_viewed'],
                    '%m/%d/%Y at %I:%M %p'
                ).isoformat()
            except:
                message['viewed_timestamp'] = None
        
        message['index'] = index
        
        return message if message else None