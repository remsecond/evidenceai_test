import os
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, Optional

# Import our modules
from parsers.pdf_parser import OFWParser
from threader.message_threader import MessageThreader
from analyzers.thread_analyzer import ThreadAnalyzer

class AnalysisPipeline:
    """Main pipeline for processing OFW documents"""
    
    STAGES = [
        "setup",
        "pdf_parsing",
        "threading",
        "analysis",
        "final"
    ]
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.checkpoint_dir = self.output_dir / "checkpoints"
        
        # Create necessary directories
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.parser = None
        self.threader = None
        self.analyzer = None
    
    def find_last_checkpoint(self) -> tuple[Optional[str], Optional[Path]]:
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
    
    def check_previous_run(self) -> Optional[str]:
        """Check for previous run and ask user what to do"""
        last_stage, last_checkpoint = self.find_last_checkpoint()
        
        if last_stage:
            print(f"\nFound previous analysis checkpoint from stage: {last_stage}")
            print(f"Timestamp: {datetime.fromtimestamp(last_checkpoint.stat().st_mtime)}")
            
            while True:
                choice = input("""
Would you like to:
1. Continue from last checkpoint
2. Start fresh
3. Exit
Choice (1-3): """)
                
                if choice == "1":
                    return last_stage
                elif choice == "2":
                    return None
                elif choice == "3":
                    sys.exit(0)
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
        
        return None
    
    def run(self, start_from_checkpoint: Optional[str] = None) -> Dict:
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
            
            results = {}
            for stage in self.STAGES:
                if stage in stages_to_run:
                    print(f"{stage:<15} {'Running...':<10}", end='\r')
                    
                    # Run stage
                    stage_results = self._run_stage(stage, results)
                    results[stage] = stage_results
                    self._save_checkpoint(stage, stage_results)
                    
                    print(f"{stage:<15} {'Complete':<10}")
                else:
                    print(f"{stage:<15} {'Skipped':<10}")
            
            print("\nAnalysis complete! Results saved in output directory.")
            return results
            
        except Exception as e:
            print(f"\nError in pipeline: {str(e)}")
            self._save_checkpoint("error", {
                "error": str(e),
                "stage": "unknown",
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    def _run_stage(self, stage: str, previous_results: Dict) -> Dict:
        """Run a specific pipeline stage"""
        if stage == "setup":
            return self._setup()
            
        elif stage == "pdf_parsing":
            self.parser = OFWParser(next(self.input_dir.glob("*.pdf")))
            return self.parser.parse_pdf()
            
        elif stage == "threading":
            self.threader = MessageThreader()
            parsed_data = previous_results.get("pdf_parsing", {}).get("messages", [])
            return self.threader.thread_messages(parsed_data)
            
        elif stage == "analysis":
            self.analyzer = ThreadAnalyzer(previous_results["threading"])
            return self.analyzer.analyze_threads()
            
        elif stage == "final":
            return self._compile_results(previous_results)
    
    def _setup(self) -> Dict:
        """Initial setup and verification"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError("No PDF files found in input directory")
            
        return {
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
            "input_files": [f.name for f in pdf_files]
        }
    
    def _compile_results(self, stage_results: Dict) -> Dict:
        """Compile final results from all stages"""
        return {
            "metadata": {
                "completion_time": datetime.now().isoformat(),
                "stages_completed": list(stage_results.keys())
            },
            "pdf_metadata": stage_results.get("pdf_parsing", {}).get("metadata", {}),
            "thread_stats": stage_results.get("threading", {}).get("stats", {}),
            "analysis_results": stage_results.get("analysis", {})
        }
    
    def _save_checkpoint(self, stage: str, data: Dict) -> None:
        """Save checkpoint data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_file = self.checkpoint_dir / f"{stage}_{timestamp}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_checkpoint(self, stage: str) -> Optional[Dict]:
        """Load most recent checkpoint for a stage"""
        checkpoints = list(self.checkpoint_dir.glob(f"{stage}_*.json"))
        if not checkpoints:
            return None
            
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        with open(latest_checkpoint) as f:
            return json.load(f)
    
    def check_dependencies(self) -> None:
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

if __name__ == "__main__":
    # Create and run pipeline
    pipeline = AnalysisPipeline()
    results = pipeline.run()