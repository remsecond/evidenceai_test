from pathlib import Path
from .workflow import WorkflowManager, DevelopmentStage
from ..parsers.pdf_parser import OFWParser

class Pipeline:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.workflow = WorkflowManager(self.base_dir)
        
    def run(self):
        try:
            self.workflow.print_status()
            
            # Run stages
            self._setup()
            self._parse_pdfs()
            self._thread_messages()
            self._analyze_relationships()
            self._detect_topics()
            
            print("\nPipeline complete")
            
        except Exception as e:
            print(f"\nError in pipeline: {str(e)}")
            self.workflow.save_checkpoint("ERROR", {"error": str(e)})
            raise
    
    def _setup(self):
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.workflow.save_checkpoint("SETUP", {"status": "complete"})
        return True
        
    def _parse_pdfs(self):
        pdfs = list(self.input_dir.glob("*.pdf"))
        if not pdfs:
            print("No PDFs found in input directory")
            return False
            
        for pdf_path in pdfs:
            parser = OFWParser(pdf_path, self.output_dir)
            result = parser.parse()
            if result['status'] != 'success':
                return False
                
        self.workflow.save_checkpoint("PDF_PARSER", {"status": "complete"})
        return True