from pathlib import Path
from typing import Dict, List
from datetime import datetime

class OFWParser:
    """Basic parser for text files (temporary solution while we resolve PDF issues)"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        
    def parse_pdf(self) -> Dict:
        """Parse file and extract messages"""
        try:
            messages = []
            
            # For now, try to read as text
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                messages = self._parse_content(content)
            
            return {
                'status': 'success',
                'messages': messages,
                'count': len(messages)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_content(self, content: str) -> List[Dict]:
        """Parse messages from content"""
        messages = []
        current_msg = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Start of new message
            if line.startswith('From:'):
                if current_msg:
                    messages.append(current_msg)
                current_msg = {
                    'from': line[5:].strip(),
                    'to': None,
                    'subject': None,
                    'timestamp': None,
                    'content': []
                }
            elif current_msg:
                if line.startswith('To:'):
                    current_msg['to'] = line[3:].strip()
                elif line.startswith('Subject:'):
                    current_msg['subject'] = line[8:].strip()
                elif line.startswith('Sent:'):
                    try:
                        date_str = line[5:].strip()
                        dt = datetime.strptime(date_str, '%m/%d/%Y %I:%M %p')
                        current_msg['timestamp'] = dt.isoformat()
                    except:
                        current_msg['timestamp'] = line[5:].strip()
                else:
                    current_msg['content'].append(line)
        
        # Add final message
        if current_msg:
            messages.append(current_msg)
            
        # Clean up message content
        for msg in messages:
            msg['content'] = '\n'.join(msg['content'])
            
        return messages