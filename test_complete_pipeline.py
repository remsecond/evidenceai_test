"""Test complete EvidenceAI pipeline from input to LLM outputs."""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import PyPDF2
from src.processors.output_generator import OutputGenerator

class PipelineTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.output_generator = OutputGenerator(self.base_dir)
        
    def test_pipeline(self):
        """Run complete pipeline test."""
        print("\033[95m=================================\033[0m")
        print("\033[95m   Testing Complete Pipeline     \033[0m")
        print("\033[95m=================================\033[0m")
        
        # Check for input files
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            print("\033[91mNo PDF files found in input directory!\033[0m")
            return False
        
        print(f"\nFound {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"  📄 {pdf.name}")
        
        # Process each PDF
        for pdf_path in pdf_files:
            print(f"\nProcessing: {pdf_path.name}")
            print("=" * 40)
            
            try:
                # Copy PDF to tool directories
                self._copy_pdf_to_tools(pdf_path)
                
                # Extract and process content
                content = self._process_pdf(pdf_path)
                if not content:
                    continue
                    
                # Generate tool-specific outputs
                print("\nGenerating NotebookLM outputs...")
                self.output_generator.generate_notebooklm_outputs(content, pdf_path.name)
                
                print("\nGenerating LLM outputs...")
                self.output_generator.generate_llm_outputs(content, pdf_path.name)
                
                # Save raw data
                self._save_raw_data(pdf_path.stem, content)
                
                print("\033[92m✓ Processing completed successfully!\033[0m")
                
            except Exception as e:
                print(f"\033[91m✗ Error processing {pdf_path.name}: {str(e)}\033[0m")
                raise  # For debugging
    
    def _copy_pdf_to_tools(self, pdf_path):
        """Copy PDF to tool directories."""
        print("\nCopying PDF to tool directories...")
        
        # Copy to NotebookLM pdfs
        notebooklm_pdfs = self.base_dir / "ab_tools_NotebookLM" / "pdfs"
        notebooklm_pdfs.mkdir(exist_ok=True, parents=True)
        dest_path = notebooklm_pdfs / pdf_path.name
        shutil.copy2(pdf_path, dest_path)
        print(f"✓ Copied to NotebookLM: {dest_path}")
        
        # Copy to ChatGPT pdfs
        chatgpt_pdfs = self.base_dir / "ab_tools_ChatGPT" / "pdfs"
        chatgpt_pdfs.mkdir(exist_ok=True, parents=True)
        dest_path = chatgpt_pdfs / pdf_path.name
        shutil.copy2(pdf_path, dest_path)
        print(f"✓ Copied to ChatGPT: {dest_path}")
    
    def _process_pdf(self, pdf_path):
        """Extract and process PDF content."""
        print("Extracting content...")
        try:
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'filename': pdf_path.name,
                    'pages': len(pdf.pages),
                    'processed_at': datetime.now().isoformat()
                }
                
                # Extract content
                full_text = ""
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n\n"
                        print(f"  ✓ Extracted page {i}/{len(pdf.pages)}")
                
                # Parse messages
                messages = self._parse_messages(full_text)
                print(f"  ✓ Found {len(messages)} messages")
                
                return {
                    'metadata': metadata,
                    'messages': messages
                }
                
        except Exception as e:
            print(f"\033[91mError extracting content: {str(e)}\033[0m")
            return None
    
    def _parse_messages(self, content):
        """Parse individual messages from content."""
        messages = []
        # Split on "Message X of Y" pattern
        blocks = content.split("Message")[1:]  # Skip header
        
        for block in blocks:
            try:
                lines = block.strip().split('\n')
                message = {}
                
                # Parse header information
                for i, line in enumerate(lines):
                    if line.startswith("Sent:"):
                        message['sent_time'] = line.replace("Sent:", "").strip()
                    elif line.startswith("From:"):
                        message['from'] = line.replace("From:", "").strip()
                    elif line.startswith("To:"):
                        to_line = line.replace("To:", "").strip()
                        # Handle viewed timestamp
                        if "(First Viewed:" in to_line:
                            parts = to_line.split("(First Viewed:")
                            message['to'] = parts[0].strip()
                            message['first_viewed'] = parts[1].rstrip(")").strip()
                        else:
                            message['to'] = to_line
                    elif line.startswith("Subject:"):
                        message['subject'] = line.replace("Subject:", "").strip()
                        # Content starts after subject
                        content_lines = lines[i+1:]
                        message['content'] = '\n'.join(content_lines).strip()
                        break
                
                # Add ISO timestamp
                if 'sent_time' in message:
                    try:
                        dt = datetime.strptime(message['sent_time'], '%m/%d/%Y at %I:%M %p')
                        message['timestamp'] = dt.isoformat()
                    except:
                        message['timestamp'] = None
                
                if message.get('sent_time'):  # Only add if we have at least a timestamp
                    messages.append(message)
                
            except Exception as e:
                print(f"Warning: Error parsing message block: {str(e)}")
                continue
        
        return messages
    
    def _save_raw_data(self, filename, content):
        """Save raw extracted data."""
        print("\nSaving raw data...")
        
        # Save JSON data
        self.output_dir.mkdir(exist_ok=True)
        json_path = self.output_dir / f"{filename}_raw.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        print(f"✓ Raw data saved: {json_path.name}")

def main():
    """Run pipeline test."""
    tester = PipelineTester()
    
    print("\nStarting EvidenceAI Pipeline Test")
    print("=============================")
    
    try:
        tester.test_pipeline()
        
        print("\n\033[92mTest complete! Check these directories for outputs:\033[0m")
        print("\n📁 NotebookLM Analysis Files:")
        print("  - Timeline Analysis")
        print("  - Communication Patterns")
        print("  - Thread Analysis")
        print("  - Participant Interactions")
        print("  - Statistical Summary")
        
        print("\n📁 LLM Analysis Files:")
        print("  - Structured Timeline")
        print("  - Pattern Analysis")
        print("  - Analysis Prompts")
        
        print("\n📁 Raw Data:")
        print("  - Extracted message data (JSON)")
        
    except Exception as e:
        print(f"\n\033[91mError in pipeline: {str(e)}\033[0m")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()