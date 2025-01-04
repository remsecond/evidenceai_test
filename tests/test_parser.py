import pytest
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO
import PyPDF2
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.pdf_parser import OFWParser, ValidationError

class TestOFWParser:
    @pytest.fixture
    def test_dir(self):
        """Create test directories"""
        base_dir = Path("C:/Users/robmo/OneDrive/Documents/evidenceai_test/tests")
        input_dir = base_dir / "test_input"
        output_dir = base_dir / "test_output"
        
        # Create directories
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            'base': base_dir,
            'input': input_dir,
            'output': output_dir
        }
        
    @pytest.fixture
    def sample_pdf_path(self, test_dir):
        """Return path to sample PDF"""
        return test_dir['input'] / "OFW_Messages_Report_Dec.pdf"
    
    @pytest.fixture
    def parser(self, test_dir):
        """Create parser instance"""
        return OFWParser(
            test_dir['input'] / "OFW_Messages_Report_Dec.pdf",
            test_dir['output']
        )

    def test_metadata_extraction(self, parser):
        """Test metadata extraction"""
        with open(parser.input_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            metadata = parser.extract_metadata(pdf)
            
            # Check required metadata fields
            assert 'total_pages' in metadata
            assert 'generated_date' in metadata
            assert 'total_messages' in metadata
            assert 'timezone' in metadata
            assert 'participants' in metadata
            
            # Check participants structure
            assert 'parents' in metadata['participants']
            assert 'children' in metadata['participants']
            assert 'third_party' in metadata['participants']
            
            # Validate types
            assert isinstance(metadata['total_pages'], int)
            assert isinstance(metadata['total_messages'], int)
            
            # Check ISO date format
            if metadata['generated_date']:
                try:
                    datetime.fromisoformat(metadata['generated_date'])
                except ValueError:
                    pytest.fail("generated_date is not in ISO format")

    def test_message_parsing(self, parser):
        """Test individual message parsing"""
        sample_block = """
        Sent: 12/01/2024 at 01:02 AM
        From: Robert Moyer
        To: Christine Moyer (First Viewed: 12/01/2024 at 07:30 AM)
        Subject: Re: Test Subject
        
        Test message content.
        """
        
        message = parser.parse_message_block(sample_block)
        
        # Check required fields
        assert message['sent_time'] == "12/01/2024 at 01:02 AM"
        assert message['from'] == "Robert Moyer"
        assert message['to'] == "Christine Moyer"
        assert message['subject'] == "Re: Test Subject"
        assert message['content'] == "Test message content."
        assert message['first_viewed'] == "12/01/2024 at 07:30 AM"
        
        # Check timestamps
        assert message['timestamp'] is not None
        assert message['viewed_timestamp'] is not None

    def test_validation(self, parser):
        """Test PDF validation"""
        with pytest.raises(ValidationError):
            parser.validate_pdf(PyPDF2.PdfReader(BytesIO(b"Invalid PDF")))

    def test_full_parse(self, parser):
        """Test complete PDF parsing"""
        result = parser.parse_pdf()
        
        # Check status
        assert result['status'] == 'success'
        
        # Check structure
        assert 'metadata' in result
        assert 'messages' in result
        assert 'timestamp' in result
        assert 'source_file' in result
        
        # Check messages
        assert len(result['messages']) > 0
        
        # Check message structure
        first_message = result['messages'][0]
        assert 'id' in first_message
        assert 'index' in first_message
        assert 'timestamp' in first_message
        assert 'content' in first_message

    def test_error_handling(self, test_dir):
        """Test error handling with invalid input"""
        invalid_path = test_dir['input'] / "nonexistent.pdf"
        parser = OFWParser(invalid_path, test_dir['output'])
        
        result = parser.parse_pdf()
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'timestamp' in result

    def test_logging(self, parser, caplog):
        """Test logging functionality"""
        parser.parse_pdf()
        
        # Check log messages
        assert "Starting to parse" in caplog.text
        assert "Parsing completed successfully" in caplog.text
        
        # Check log file
        log_file = parser.output_dir / 'parser.log'
        assert log_file.exists()

    def test_output_generation(self, parser, test_dir):
        """Test JSON output generation"""
        parser.parse_pdf()
        
        # Check output directory
        json_dir = test_dir['output'] / 'json' / 'messages'
        assert json_dir.exists()
        
        # Check for output file
        json_files = list(json_dir.glob("parsed_messages_*.json"))
        assert len(json_files) > 0
        
        # Validate JSON structure
        with open(json_files[0]) as f:
            data = json.load(f)
            assert 'metadata' in data
            assert 'messages' in data
            assert 'status' in data

    def test_message_validation(self, parser):
        """Test message validation"""
        valid_message = {
            'sent_time': '12/01/2024 at 01:02 AM',
            'from': 'Sender',
            'to': 'Recipient',
            'content': 'Test content'
        }
        
        invalid_message = {
            'sent_time': '12/01/2024 at 01:02 AM',
            'from': 'Sender'
            # Missing required fields
        }
        
        assert parser.validate_message(valid_message) is True
        assert parser.validate_message(invalid_message) is False

if __name__ == '__main__':
    pytest.main([__file__])