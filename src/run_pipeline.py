import sys
from pathlib import Path
from datetime import datetime
import logging
import traceback

# Add src directory to path
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from parsers.pdf_parser import OFWParser
from formatters.llm_formatter import LLMFormatter

def setup_logging(base_dir: Path) -> None:
    """Setup logging configuration"""
    log_dir = base_dir / "output" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def run_pipeline(input_file: str) -> None:
    """Run the complete analysis pipeline"""
    try:
        # Setup paths
        base_dir = Path(__file__).parent.parent
        input_path = base_dir / "input" / input_file
        
        # Setup logging
        setup_logging(base_dir)
        logger = logging.getLogger('pipeline')
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        logger.info(f"Starting analysis of {input_file}")
        logger.info("-" * 50)
        
        # Step 1: Parse PDF
        logger.info("Step 1: Parsing PDF...")
        parser = OFWParser(input_path)
        parse_results = parser.parse_pdf()
        
        if parse_results.get('status') == 'error':
            raise Exception(f"PDF parsing failed: {parse_results.get('error')}")
            
        logger.info(f"Successfully parsed {len(parse_results['messages'])} messages")
        
        # Step 2: Format for LLM
        logger.info("Step 2: Formatting messages...")
        formatter = LLMFormatter(base_dir)
        formatted = formatter.format_messages(parse_results['messages'])
        
        if 'error' in formatted:
            raise Exception(f"Formatting failed: {formatted['error']}")
        
        # Print summary
        logger.info("\nAnalysis Complete!")
        logger.info("-" * 50)
        logger.info(f"Total Messages: {formatted['metadata']['total_messages']}")
        logger.info(f"Date Range: {formatted['metadata']['date_range']['start']} to {formatted['metadata']['date_range']['end']}")
        logger.info(f"Thread Count: {formatted['statistics']['thread_statistics']['total_threads']}")
        logger.info("Results saved in output/llm_formatted/")
        
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_pipeline.py <pdf_filename>")
        sys.exit(1)
        
    run_pipeline(sys.argv[1])