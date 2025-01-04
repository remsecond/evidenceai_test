"""Process OFW PDF and generate LLM-ready outputs."""
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
        self.notebooklm_dir = self.base_dir / "ab_tools_NotebookLM"
        self.chatgpt_dir = self.base_dir / "ab_tools_ChatGPT"
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.notebooklm_dir.mkdir(exist_ok=True)
        self.chatgpt_dir.mkdir(exist_ok=True)
        
    def process_pdf(self, pdf_name):
        """Process PDF and generate all outputs."""
        pdf_path = self.input_dir / pdf_name
        print(f"\nProcessing: {pdf_path}")
        
        try:
            # Read and parse PDF
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                print(f"Pages found: {len(pdf.pages)}")
                
                # Extract text and parse messages
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                
                messages = self._extract_messages(full_text)
                print(f"Messages found: {len(messages)}")
                
                # Generate all outputs
                self._save_raw_messages(pdf_name, messages)
                self._generate_notebooklm_docs(pdf_name, messages)
                self._generate_llm_docs(pdf_name, messages)
                
                print(f"\nProcessing complete! Check the output directories:")
                print(f"- Raw data: {self.output_dir}")
                print(f"- NotebookLM: {self.notebooklm_dir}")
                print(f"- ChatGPT/Claude: {self.chatgpt_dir}")
                return True
                
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return False
    
    def _extract_messages(self, text):
        """Extract individual messages from text."""
        messages = []
        blocks = re.split(r'Message \d+ of \d+', text)[1:]
        
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
    
    def _save_raw_messages(self, pdf_name, messages):
        """Save raw JSON data."""
        output_file = self.output_dir / f"{Path(pdf_name).stem}_messages.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_at': datetime.now().isoformat(),
                'source_file': pdf_name,
                'message_count': len(messages),
                'messages': messages
            }, f, indent=2)
    
    def _generate_notebooklm_docs(self, pdf_name, messages):
        """Generate NotebookLM formatted documents."""
        # Create main summary document
        summary_file = self.notebooklm_dir / f"{Path(pdf_name).stem}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("OFW Communications Analysis\n")
            f.write("==========================\n\n")
            f.write(f"Source: {pdf_name}\n")
            f.write(f"Messages: {len(messages)}\n")
            f.write(f"Date Range: {messages[0]['sent_time']} to {messages[-1]['sent_time']}\n\n")
            
            # Add participant summary
            participants = set()
            for msg in messages:
                participants.add(msg['from'])
                participants.add(msg['to'])
            
            f.write("Participants:\n")
            for p in sorted(participants):
                f.write(f"- {p}\n")
        
        # Create chronological message log
        log_file = self.notebooklm_dir / f"{Path(pdf_name).stem}_messages.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            for i, msg in enumerate(messages, 1):
                f.write(f"\nMessage {i}\n")
                f.write("-" * 50 + "\n")
                f.write(f"From: {msg['from']}\n")
                f.write(f"To: {msg['to']}\n")
                f.write(f"Sent: {msg['sent_time']}\n")
                if msg.get('subject'):
                    f.write(f"Subject: {msg['subject']}\n")
                if msg.get('first_viewed'):
                    f.write(f"First Viewed: {msg['first_viewed']}\n")
                f.write("\nContent:\n")
                f.write(msg['content'])
                f.write("\n" + "=" * 50 + "\n")
    
    def _generate_llm_docs(self, pdf_name, messages):
        """Generate ChatGPT/Claude optimized documents."""
        output_file = self.chatgpt_dir / f"{Path(pdf_name).stem}_for_analysis.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("OFW MESSAGE ANALYSIS DATA\n")
            f.write("=========================\n\n")
            
            # Add metadata in easily parseable format
            f.write("METADATA:\n")
            f.write(f"File: {pdf_name}\n")
            f.write(f"Total Messages: {len(messages)}\n")
            f.write(f"Date Range: {messages[0]['sent_time']} to {messages[-1]['sent_time']}\n\n")
            
            # Write messages in a format optimized for LLM analysis
            f.write("MESSAGES:\n\n")
            for i, msg in enumerate(messages, 1):
                f.write(f"[Message {i}]\n")
                f.write(f"Timestamp: {msg['sent_time']}\n")
                f.write(f"From: {msg['from']}\n")
                f.write(f"To: {msg['to']}\n")
                if msg.get('subject'):
                    f.write(f"Subject: {msg['subject']}\n")
                if msg.get('first_viewed'):
                    f.write(f"First Viewed: {msg['first_viewed']}\n")
                f.write("\nContent:\n")
                f.write(msg['content'])
                f.write("\n\n---\n\n")

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