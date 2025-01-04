"""Logging configuration for EvidenceAI pipeline."""
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(base_dir: Path):
    """Configure logging with both file and console output."""
    # Create logs directory
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    logger = logging.getLogger("evidenceai")
    logger.info("Starting EvidenceAI Pipeline")
    logger.info(f"Log file: {log_file}")
    
    return logger