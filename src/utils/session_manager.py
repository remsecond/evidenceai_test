"""
Evidence Analysis Session Manager
-------------------------------
Handles session management, file tracking, and pipeline management for evidence analysis.

Author: EvidenceAI Team
Date: January 2025
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path

# Constants
DEFAULT_LOG_DIR = "logs"
MIN_DISK_SPACE_GB = 50.0
INPUT_DIR = "input"  # Added input directory constant

class Logger:
    """Simple logging implementation."""
    
    def __init__(self, name: str):
        self.name = name
        log_dir = Path(DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        self.log_file = log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def info(self, message: str):
        """Log info level message."""
        self._log("INFO", message)
        
    def error(self, message: str):
        """Log error level message."""
        self._log("ERROR", message)
        
    def debug(self, message: str):
        """Log debug level message."""
        self._log("DEBUG", message)
        
    def _log(self, level: str, message: str):
        """Write log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {self.name} - {level}: {message}"
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
        
        # Print to console
        if level in ['INFO', 'ERROR']:
            print(f"{level}: {message}")

class PipelineStage(Enum):
    """Enum defining the stages of the evidence analysis pipeline."""
    FILE_VALIDATION = "Input File Validation"
    DOC_PROCESSING = "Document Processing" 
    THREAD_ANALYSIS = "Thread Analysis"
    PATTERN_DETECTION = "Pattern Detection"
    TIMELINE_GENERATION = "Timeline Generation"
    REPORT_CREATION = "Report Creation"

@dataclass
class InputFile:
    """Data class representing an input file for analysis."""
    name: str
    size: float  # in MB
    created_date: datetime
    path: str
    validated: bool = False

@dataclass
class SessionState:
    """Data class representing the state of an analysis session."""
    session_id: str
    created_at: datetime
    last_session: Optional[str]
    input_files: List[InputFile]
    active_stages: List[PipelineStage]
    selected_deliverables: List[str]
    status: str = "PENDING"

class SessionManager:
    """Main class for managing evidence analysis sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self.logger = Logger('SessionManager')
        self.current_session = None
        self.input_dir = Path(INPUT_DIR)
        
        if not self.input_dir.exists():
            self.logger.info(f"Creating input directory: {INPUT_DIR}")
            self.input_dir.mkdir(exist_ok=True)
            
        self.logger.info("Session manager initialized")

    def create_session(self) -> SessionState:
        """Create and initialize a new analysis session."""
        try:
            session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.logger.info(f"Creating new session: {session_id}")
            
            input_files = self._scan_input_files()
            self.current_session = SessionState(
                session_id=session_id,
                created_at=datetime.now(),
                last_session=self._get_last_session(),
                input_files=input_files,
                active_stages=list(PipelineStage),
                selected_deliverables=self._get_default_deliverables()
            )
            
            return self.current_session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            raise

    def _scan_input_files(self) -> List[InputFile]:
        """Scan input directory for PDF files."""
        self.logger.info("Scanning for input files...")
        input_files = []
        
        try:
            # Make sure input directory exists
            if not self.input_dir.exists():
                self.logger.info(f"Creating input directory: {INPUT_DIR}")
                self.input_dir.mkdir(exist_ok=True)
            
            # Scan for PDF files
            for file_path in self.input_dir.glob("*.pdf"):
                stats = file_path.stat()
                input_file = InputFile(
                    name=file_path.name,
                    size=stats.st_size / (1024 * 1024),
                    created_date=datetime.fromtimestamp(stats.st_ctime),
                    path=str(file_path.absolute())
                )
                input_files.append(input_file)
                self.logger.info(f"Found file: {input_file.name} ({input_file.size:.1f} MB)")
            
            if not input_files:
                self.logger.info(f"No PDF files found in {INPUT_DIR} directory")
                
            return input_files
            
        except Exception as e:
            self.logger.error(f"Error scanning input files: {str(e)}")
            raise

    def _get_last_session(self) -> Optional[str]:
        """Get the ID of the last session if it exists."""
        try:
            # Look for last_session.txt file
            last_session_file = Path("last_session.txt")
            if last_session_file.exists():
                return last_session_file.read_text().strip()
            return None
        except Exception as e:
            self.logger.error(f"Error getting last session: {str(e)}")
            return None

    def _get_default_deliverables(self) -> List[str]:
        """Get list of default deliverable files."""
        return [
            "timeline_analysis.txt",
            "communication_patterns.json",
            "participant_summary.json",
            "statistical_summary.json",
            "final_report.pdf"
        ]

    def validate_environment(self) -> Dict[str, bool]:
        """Validate system environment and dependencies."""
        self.logger.info("Validating environment...")
        
        try:
            results = {
                "disk_space": self._check_disk_space(),
                "input_dir": self.input_dir.exists(),
                "input_files": bool(self.current_session and self.current_session.input_files)
            }
            
            for check, status in results.items():
                self.logger.info(f"{check}: {'✓' if status else '✗'}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {str(e)}")
            raise

    def _check_disk_space(self) -> bool:
        """Check if sufficient disk space is available."""
        try:
            if sys.platform == 'win32':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.getcwd()),
                    None, None,
                    ctypes.pointer(free_bytes)
                )
                free_gb = free_bytes.value / (1024**3)
            else:
                stats = os.statvfs('.')
                free_gb = (stats.f_bavail * stats.f_frsize) / (1024**3)
            
            self.logger.debug(f"Free disk space: {free_gb:.1f} GB")
            return free_gb >= MIN_DISK_SPACE_GB
            
        except Exception as e:
            self.logger.error(f"Error checking disk space: {str(e)}")
            return False

    def get_session_summary(self) -> str:
        """Generate a formatted summary of the current session."""
        if not self.current_session:
            return "No active session"

        summary = [
            "\n========== Evidence Analysis Session Summary ==========",
            f"Session ID: {self.current_session.session_id}",
            f"Created At: {self.current_session.created_at}",
            f"Last Session: {self.current_session.last_session or 'None'}",
            "\nInput Files:",
            *[f"- {f.name} ({f.size:.1f} MB)" for f in self.current_session.input_files],
            "\nActive Pipeline Stages:",
            *[f"- {stage.value}" for stage in self.current_session.active_stages],
            "\nDeliverables:",
            *[f"- {d}" for d in self.current_session.selected_deliverables],
            "=================================================="
        ]
        
        return "\n".join(summary)

def main():
    """Main entry point for the session manager."""
    try:
        # Initialize session manager
        manager = SessionManager()
        
        # Create new session
        session = manager.create_session()
        
        # Validate environment
        validation = manager.validate_environment()
        if not all(validation.values()):
            print("Environment validation failed! Please check the following:")
            print("1. Ensure there are PDF files in the 'input' directory")
            print("2. Ensure sufficient disk space is available")
            sys.exit(1)
        
        # Print session summary
        print(manager.get_session_summary())
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()