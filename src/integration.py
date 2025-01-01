"""Integration module for the threading system."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

from .parsers.pdf_parser import OFWParser
from .threader.chain_builder import MessageThreader
from .validators.thread_validator import ThreadValidator
from .logging.airtable_logger import AirtableLogger

class ThreadingOrchestrator:
    """Orchestrates the threading process."""
    
    def __init__(self, input_dir: Union[str, Path], output_dir: Union[str, Path],
                 airtable_base_id: Optional[str] = None,
                 airtable_api_key: Optional[str] = None):
        # Directory setup
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = self.output_dir / "checkpoints"
        
        # Create necessary directories
        self.output_dir.mkdir(exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.parser = OFWParser(self.input_dir)
        self.threader = MessageThreader()
        self.validator = ThreadValidator()
        self.logger = AirtableLogger(airtable_base_id, airtable_api_key)
        
        # Setup logging
        self.log = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.output_dir / "threading.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def process_file(self, filename: str, checkpoint: bool = True) -> Dict:
        """Process a single file through the pipeline."""
        try:
            start_time = datetime.now()
            self.log.info(f"Starting processing of {filename}")
            
            results = {
                'status': 'success',
                'filename': filename,
                'timestamp': start_time.isoformat(),
                'stages': {}
            }
            
            # Stage 1: Parse PDF
            self.log.info("Stage 1: Parsing PDF")
            parse_results = self.parser.parse_pdf(filename)
            if checkpoint:
                self._save_checkpoint('parsing', parse_results)
            results['stages']['parsing'] = {
                'status': 'success',
                'message_count': len(parse_results.get('messages', []))
            }
            
            # Stage 2: Thread Messages
            self.log.info("Stage 2: Threading messages")
            threads = self.threader.process_messages(parse_results['messages'])
            thread_metadata = self.threader.get_thread_metadata()
            if checkpoint:
                self._save_checkpoint('threading', {
                    'threads': threads,
                    'metadata': thread_metadata
                })
            results['stages']['threading'] = {
                'status': 'success',
                'thread_count': len(threads)
            }
            
            # Stage 3: Validate Results
            self.log.info("Stage 3: Validating results")
            validation_results = self.validator.validate_threading_results(
                threads, thread_metadata
            )
            if checkpoint:
                self._save_checkpoint('validation', validation_results)
            results['stages']['validation'] = {
                'status': 'success' if validation_results['valid'] else 'warnings',
                'error_count': len(validation_results['errors']),
                'warning_count': len(validation_results['warnings'])
            }
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            results['processing_time'] = processing_time
            
            # Compile statistics
            results['statistics'] = {
                'messages': results['stages']['parsing']['message_count'],
                'threads': results['stages']['threading']['thread_count'],
                'thread_stats': self.threader.get_thread_statistics()
            }
            
            # Log to Airtable
            self.logger.log_processing(filename, results)
            self.logger.log_validation(filename, validation_results)
            self.logger.log_metadata(filename, thread_metadata)
            
            # Save final results
            self._save_results(filename, results, threads, thread_metadata, validation_results)
            
            self.log.info(f"Completed processing of {filename}")
            return results
            
        except Exception as e:
            self.log.error(f"Error processing {filename}: {str(e)}", exc_info=True)
            results = {
                'status': 'error',
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            self._save_error_report(filename, results)
            return results
    
    def _save_checkpoint(self, stage: str, data: Dict):
        """Save a checkpoint for a processing stage."""
        checkpoint_file = self.checkpoint_dir / f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _save_results(self, filename: str, results: Dict, threads: Dict, 
                     metadata: Dict, validation: Dict):
        """Save final processing results."""
        # Create results directory
        results_dir = self.output_dir / filename.replace('.pdf', '')
        results_dir.mkdir(exist_ok=True)
        
        # Save components
        with open(results_dir / 'summary.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        with open(results_dir / 'threads.json', 'w', encoding='utf-8') as f:
            json.dump(threads, f, indent=2)
            
        with open(results_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        with open(results_dir / 'validation.json', 'w', encoding='utf-8') as f:
            json.dump(validation, f, indent=2)
    
    def _save_error_report(self, filename: str, error_data: Dict):
        """Save error report for failed processing."""
        error_file = self.output_dir / f"error_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)