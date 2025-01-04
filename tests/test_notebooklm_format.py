import pytest
from pathlib import Path
import json
from datetime import datetime
import sys
import os

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.pdf_parser import OFWParser

class TestNotebookLMFormat:
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
    def sample_thread(self):
        """Create a sample message thread"""
        return {
            'thread_id': 'thread_001',
            'topic': 'Scheduling',
            'messages': [
                {
                    'id': 'msg_001',
                    'timestamp': '2024-12-01T01:02:00',
                    'from': 'Person A',
                    'to': 'Person B',
                    'subject': 'Weekend Schedule',
                    'content': 'Can we discuss the weekend schedule?'
                },
                {
                    'id': 'msg_002',
                    'timestamp': '2024-12-01T02:15:00',
                    'from': 'Person B',
                    'to': 'Person A',
                    'subject': 'Re: Weekend Schedule',
                    'content': 'Yes, what time works for you?'
                }
            ]
        }

    def test_thread_format(self, sample_thread):
        """Test NotebookLM thread format"""
        formatted_output = self.format_thread_for_notebooklm(sample_thread)
        
        # Check required sections
        assert '# Conversation Thread: Scheduling' in formatted_output
        assert 'Date: 2024-12-01' in formatted_output
        assert 'Participants: Person A, Person B' in formatted_output
        
        # Check message format
        assert '[Person A] 01:02 AM - Can we discuss the weekend schedule?' in formatted_output
        assert '[Person B] 02:15 AM - Yes, what time works for you?' in formatted_output

    def test_participant_summary(self, sample_thread):
        """Test participant summary generation"""
        summary = self.generate_participant_summary(sample_thread)
        
        assert 'Participants:' in summary
        assert 'Person A' in summary
        assert 'Person B' in summary
        assert len(summary.split('\n')) >= 2  # At least header and participants

    def test_message_chronology(self, sample_thread):
        """Test chronological message ordering"""
        formatted_output = self.format_thread_for_notebooklm(sample_thread)
        
        # Split into lines and find message timestamps
        lines = formatted_output.split('\n')
        message_lines = [l for l in lines if l.strip().startswith('[')]
        
        # Check chronological order
        timestamps = []
        for line in message_lines:
            time_str = line.split(']')[1].split('-')[0].strip()
            timestamps.append(datetime.strptime(time_str, '%I:%M %p'))
            
        assert timestamps == sorted(timestamps)

    def test_thread_summary(self, sample_thread):
        """Test thread summary generation"""
        summary = self.generate_thread_summary(sample_thread)
        
        assert sample_thread['topic'] in summary
        assert str(len(sample_thread['messages'])) in summary
        assert 'messages between' in summary
        assert 'Person A' in summary and 'Person B' in summary

    def test_formatting_edge_cases(self):
        """Test handling of edge cases in formatting"""
        edge_cases = {
            'empty_thread': {
                'thread_id': 'thread_002',
                'topic': 'Empty',
                'messages': []
            },
            'missing_subject': {
                'thread_id': 'thread_003',
                'topic': 'No Subject',
                'messages': [{
                    'id': 'msg_003',
                    'timestamp': '2024-12-01T03:00:00',
                    'from': 'Person A',
                    'to': 'Person B',
                    'content': 'Test message'
                }]
            },
            'long_content': {
                'thread_id': 'thread_004',
                'topic': 'Long Message',
                'messages': [{
                    'id': 'msg_004',
                    'timestamp': '2024-12-01T04:00:00',
                    'from': 'Person A',
                    'to': 'Person B',
                    'content': 'A' * 1000  # Very long message
                }]
            }
        }
        
        for case_name, thread in edge_cases.items():
            formatted = self.format_thread_for_notebooklm(thread)
            
            if case_name == 'empty_thread':
                assert 'No messages' in formatted
            elif case_name == 'missing_subject':
                assert '[Person A]' in formatted
                assert 'Test message' in formatted
            elif case_name == 'long_content':
                assert len(formatted) <= 2000  # Check length limit

    def format_thread_for_notebooklm(self, thread):
        """Format a thread for NotebookLM consumption"""
        if not thread['messages']:
            return f"# Conversation Thread: {thread['topic']}\nNo messages in thread"
            
        # Get thread date from first message
        first_msg = thread['messages'][0]
        thread_date = datetime.fromisoformat(first_msg['timestamp']).strftime('%Y-%m-%d')
        
        # Get unique participants
        participants = set()
        for msg in thread['messages']:
            participants.add(msg['from'])
            participants.add(msg['to'])
        
        # Build output
        output = []
        output.append(f"# Conversation Thread: {thread['topic']}")
        output.append(f"Date: {thread_date}")
        output.append(f"Participants: {', '.join(sorted(participants))}")
        output.append("")
        
        # Add messages
        for msg in thread['messages']:
            timestamp = datetime.fromisoformat(msg['timestamp'])
            time_str = timestamp.strftime('%I:%M %p')
            output.append(f"[{msg['from']}] {time_str} - {msg['content']}")
            
        return '\n'.join(output)

    def generate_participant_summary(self, thread):
        """Generate participant summary for thread"""
        participants = set()
        for msg in thread['messages']:
            participants.add(msg['from'])
            participants.add(msg['to'])
            
        return f"Participants:\n{', '.join(sorted(participants))}"

    def generate_thread_summary(self, thread):
        """Generate thread summary"""
        if not thread['messages']:
            return f"Empty thread on topic: {thread['topic']}"
            
        participants = set()
        for msg in thread['messages']:
            participants.add(msg['from'])
            participants.add(msg['to'])
            
        return (
            f"Thread '{thread['topic']}' contains {len(thread['messages'])} "
            f"messages between {', '.join(sorted(participants))}"
        )

if __name__ == '__main__':
    pytest.main([__file__])