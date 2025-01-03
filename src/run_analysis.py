import os
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

from parsers.pdf_parser import OFWParser
from analyzers.message_threader import MessageThreader

class AnalysisPipeline:
    STAGES = [
        "setup",
        "pdf_parsing",
        "threading",
        "relationships",
        "topics",
        "final"
    ]
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.checkpoint_dir = self.output_dir / "checkpoints"
        
        # Set up logging
        logging.basicConfig(
            filename=self.output_dir / 'analysis.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def find_last_checkpoint(self):
        """Find the most recent checkpoint"""
        latest_checkpoint = None
        latest_time = 0
        latest_stage = None
        
        for stage in self.STAGES:
            checkpoints = list(self.checkpoint_dir.glob(f"{stage}_*.json"))
            if checkpoints:
                checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
                if checkpoint.stat().st_mtime > latest_time:
                    latest_time = checkpoint.stat().st_mtime
                    latest_checkpoint = checkpoint
                    latest_stage = stage
                    
        return latest_stage, latest_checkpoint

    def check_previous_run(self):
        """Check for previous run and ask user what to do"""
        last_stage, last_checkpoint = self.find_last_checkpoint()
        
        if last_stage:
            print(f"\nFound previous analysis checkpoint from stage: {last_stage}")
            print(f"Timestamp: {datetime.fromtimestamp(last_checkpoint.stat().st_mtime)}")
            
            while True:
                choice = input("\nWould you like to:\n1. Continue from last checkpoint\n2. Start fresh\n3. Exit\nChoice (1-3): ")
                if choice == "1":
                    return last_stage
                elif choice == "2":
                    return None
                elif choice == "3":
                    sys.exit(0)
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
                    
        return None

    def run(self, start_from_checkpoint=None):
        """Run the complete analysis pipeline"""
        try:
            # Check dependencies first
            self.check_dependencies()
            
            # If no checkpoint specified, check for previous run
            if start_from_checkpoint is None:
                start_from_checkpoint = self.check_previous_run()
                
            # Show progress
            print("\nStarting analysis pipeline...")
            print(f"{'Stage':<15} {'Status':<10}")
            print("-" * 25)
            
            stages_to_run = self.STAGES[self.STAGES.index(start_from_checkpoint) if start_from_checkpoint else 0:]
            
            for stage in self.STAGES:
                if stage in stages_to_run:
                    print(f"{stage:<15} {'Running...':<10}", end='\r')
                    # Run stage
                    results = self._run_stage(stage)
                    self._save_checkpoint(stage, results)
                    print(f"{stage:<15} {'Complete':<10}")
                else:
                    print(f"{stage:<15} {'Skipped':<10}")
                    
            print("\nAnalysis complete! Results saved in output directory.")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in pipeline: {str(e)}")
            print(f"\nError in pipeline: {str(e)}")
            self._save_checkpoint("error", {
                "error": str(e),
                "stage": "unknown",
                "timestamp": datetime.now().isoformat()
            })
            raise

    def check_dependencies(self):
        """Check if all required packages are installed"""
        required_packages = ['PyPDF2', 'pandas', 'numpy']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            print("\nMissing required packages. Please install:")
            print("pip install " + " ".join(missing_packages))
            sys.exit(1)

    def _run_stage(self, stage):
        """Run a specific pipeline stage"""
        self.logger.info(f"Running stage: {stage}")
        
        try:
            if stage == "setup":
                return self._setup()
            elif stage == "pdf_parsing":
                return self._parse_pdf()
            elif stage == "threading":
                return self._thread_messages(self.load_checkpoint("pdf_parsing"))
            elif stage == "relationships":
                return self._analyze_relationships(self.load_checkpoint("threading"))
            elif stage == "topics":
                return self._detect_topics(self.load_checkpoint("relationships"))
            elif stage == "final":
                return self._compile_results(
                    self.load_checkpoint("pdf_parsing"),
                    self.load_checkpoint("threading"),
                    self.load_checkpoint("relationships"),
                    self.load_checkpoint("topics")
                )
        except Exception as e:
            self.logger.error(f"Error in stage {stage}: {str(e)}")
            raise

    def _setup(self):
        """Initial setup and verification"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        
        return {
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
            "input_files": [f.name for f in pdf_files]
        }

    def _parse_pdf(self):
        """Parse PDF files"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            raise ValueError("No PDF files found in input directory")
            
        # For now, just process the first PDF
        pdf_file = pdf_files[0]
        parser = OFWParser(pdf_file)
        return parser.parse_pdf()

    def _thread_messages(self, parse_results):
        """Thread messages into conversations"""
        if parse_results["status"] != "success":
            raise ValueError("Cannot thread messages - parsing was unsuccessful")
            
        threader = MessageThreader(logger=self.logger)
        return threader.thread_messages(parse_results["messages"])

    def _analyze_relationships(self, thread_results):
        """Analyze relationships in threaded messages"""
        # TODO: Implement relationship analysis
        return {}

    def _detect_topics(self, relationship_results):
        """Detect topics in messages"""
        # TODO: Implement topic detection
        return {}

    def _compile_results(self, *args):
        """Compile all results into final analysis"""
        # TODO: Implement results compilation
        return {}

    def _save_checkpoint(self, stage, data):
        """Save checkpoint data"""
        checkpoint_file = self.checkpoint_dir / f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        self.logger.info(f"Saved checkpoint for stage {stage}: {checkpoint_file}")

    def load_checkpoint(self, stage):
        """Load most recent checkpoint for a stage"""
        checkpoints = list(self.checkpoint_dir.glob(f"{stage}_*.json"))
        
        if not checkpoints:
            raise ValueError(f"No checkpoint found for stage: {stage}")
            
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        
        with open(latest_checkpoint) as f:
            return json.load(f)

if __name__ == "__main__":
    # Create and run pipeline
    pipeline = AnalysisPipeline()
    results = pipeline.run()