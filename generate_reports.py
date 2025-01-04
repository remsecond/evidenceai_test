"""
OFW Message Analysis Report Generator
----------------------------------
Analyzes OFW messages and generates reports suitable for LLM analysis.
"""

from src.utils.analyze_timeline import TimelineAnalyzer
import logging
from pathlib import Path

def main():
    """Main execution function."""
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    logger = logging.getLogger('ReportGenerator')

    try:
        # Initialize analyzer
        analyzer = TimelineAnalyzer()
        
        # Process messages and generate reports
        logger.info("Starting report generation...")
        success = analyzer.process_messages()
        
        if success:
            # List generated files
            output_files = [
                'timeline_analysis.txt',
                'communication_patterns.json',
                'participant_summary.json',
                'statistical_summary.json',
                'final_report.txt'
            ]
            
            logger.info("\nGenerated Reports:")
            for file in output_files:
                path = Path('output') / file
                if path.exists():
                    logger.info(f"✓ {file}")
                else:
                    logger.warning(f"✗ {file} not found")
            
            logger.info("\nLLM-Ready Formats:")
            logger.info("- NotebookLM: ab_tools_NotebookLM/")
            logger.info("- ChatGPT/Claude: ab_tools_ChatGPT/")
            
        else:
            logger.error("Report generation failed - check logs for details")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())