"""Process input files."""
import os
import logging
from datetime import datetime
import PyPDF2
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evidenceai")

class FileProcessor:
    """Process input files and extract content."""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.logger = logger
    
    def process_pdf(self, filepath):
        """Process a PDF file and extract metadata."""
        try:
            file_stats = os.stat(filepath)
            
            with open(filepath, 'rb') as pdf_file:
                pdf = PyPDF2.PdfReader(pdf_file)
                page_count = len(pdf.pages)
                
                # Read first page
                first_page = pdf.pages[0].extract_text()
                
                metadata = {
                    'filename': os.path.basename(filepath),
                    'file_size': file_stats.st_size,
                    'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    'page_count': page_count,
                    'first_page_preview': first_page[:500] if first_page else None
                }
                
                self.logger.info(f"Processed file: {metadata['filename']}")
                return metadata
                
        except Exception as e:
            self.logger.error(f"Error processing file {filepath}: {str(e)}")
            raise
            
    def extract_text(self, pdf_path):
        """Extract text from PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise