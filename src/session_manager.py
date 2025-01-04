from pathlib import Path
from datetime import datetime
import json
import os

class SessionManager:
    """Manages EvidenceAI processing sessions"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.sessions_dir = self.base_dir / "sessions"
        self.input_dir = self.base_dir / "input"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
    def create_session(self) -> dict:
        """Create new session with current status"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session = {
            'session_id': f'session_{timestamp}',
            'created_at': datetime.now().isoformat(),
            'input_files': self._get_input_files(),
            'status': 'initialized',
            'progress': {
                'pdf_parsing': 'pending',
                'thread_analysis': 'pending',
                'llm_formatting': 'pending',
                'output_generation': 'pending'
            },
            'requirements': self._get_base_requirements()
        }
        
        # Save session
        session_file = self.sessions_dir / f'SESSION_{timestamp}.json'
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
            
        # Generate markdown summary
        self._generate_session_md(session)
        
        return session
    
    def _get_input_files(self) -> dict:
        """Get information about files in input directory"""
        files = {}
        if self.input_dir.exists():
            for file in self.input_dir.glob('*'):
                if file.is_file():
                    files[file.name] = {
                        'size_mb': round(file.stat().st_size / (1024 * 1024), 2),
                        'last_modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    }
        return files
    
    def _get_base_requirements(self) -> dict:
        """Get base processing requirements"""
        return {
            'file_processing': {
                'maintain_context': True,
                'preserve_timestamps': True,
                'handle_encoding': True,
                'clean_formatting': True
            },
            'data_structure': {
                'thread_mapping': True,
                'relationships': True,
                'cross_references': True,
                'temporal_alignment': True
            },
            'output_format': {
                'notebooklm_compatible': True,
                'statistical_analysis': True,
                'pattern_detection': True
            }
        }
    
    def _generate_session_md(self, session: dict) -> None:
        """Generate markdown summary of session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        md_file = self.base_dir / f'SESSION_PROMPT_{timestamp}.md'
        
        with open(md_file, 'w') as f:
            f.write("# EvidenceAI Session: LLM Output Processing\n")
            f.write("========================================\n")
            
            # Overview
            f.write("## Overview\n")
            f.write("This session focuses on converting OFW message data and custody schedules ")
            f.write("into formats optimized for NotebookLM and other LLM analysis platforms.\n\n")
            
            # Input Files
            f.write("## Input Files Status\n")
            f.write("Currently detected in input/:\n")
            for filename, info in session['input_files'].items():
                f.write(f"- {filename} ({info['size_mb']} MB)\n")
            
            if not any(f.lower().endswith('.pdf') for f in session['input_files']):
                f.write("- Requiring OFW message export PDF\n")
            if not any('schedule' in f.lower() for f in session['input_files']):
                f.write("- Requiring custody schedule file\n")
            f.write("\n")
            
            # Processing Steps
            f.write("## Required Processing Steps\n")
            f.write("1. Text Extraction & Cleaning\n")
            f.write("   - Convert PDF content to clean text\n")
            f.write("   - Standardize date/time formats\n")
            f.write("   - Remove irrelevant system metadata\n")
            f.write("   - Structure message threads\n\n")
            
            f.write("2. Data Organization\n")
            f.write("   - Message chronological sorting\n")
            f.write("   - Thread relationship mapping\n")
            f.write("   - Participant identification\n")
            f.write("   - Event timeline construction\n\n")
            
            f.write("3. NotebookLM Format Preparation\n")
            f.write("   - Split content into appropriate chunk sizes\n")
            f.write("   - Add metadata headers\n")
            f.write("   - Create contextual summaries\n")
            f.write("   - Generate embeddings\n\n")
            
            f.write("4. Analysis Format Generation\n")
            f.write("   - Create timeline_analysis.txt\n")
            f.write("     - Key events\n")
            f.write("     - Date patterns\n")
            f.write("     - Communication trends\n")
            f.write("   \n")
            f.write("   - Generate communication_patterns.json\n")
            f.write("     - Message frequency\n")
            f.write("     - Response patterns\n")
            f.write("     - Topic clustering\n")
            f.write("   \n")
            f.write("   - Build participant_summary.json\n")
            f.write("     - Participant roles\n")
            f.write("     - Interaction patterns\n")
            f.write("     - Communication styles\n")
            f.write("   \n")
            f.write("   - Compile statistical_summary.json\n")
            f.write("     - Message volumes\n")
            f.write("     - Response times\n")
            f.write("     - Topic distribution\n")
            f.write("   \n")
            f.write("   - Produce final_report.pdf\n")
            f.write("     - Executive summary\n")
            f.write("     - Key findings\n")
            f.write("     - Pattern analysis\n")
            f.write("     - Recommendations\n\n")
            
            # Requirements
            f.write("## Session Requirements\n")
            f.write("### File Processing\n")
            f.write("- Maintain original message context\n")
            f.write("- Preserve timestamp accuracy\n")
            f.write("- Handle encoded characters\n")
            f.write("- Clean formatting artifacts\n")
            
            f.write("### Data Structure\n")
            f.write("- Thread ID mapping\n")
            f.write("- Parent-child relationships\n")
            f.write("- Cross-reference capabilities\n")
            f.write("- Temporal alignment\n")
            
            f.write("### Output Format\n")
            f.write("- NotebookLM compatible\n")