"""Generate structured outputs for NotebookLM and LLMs."""
from pathlib import Path
from datetime import datetime
import json
from .timeline_generator import TimelineGenerator

class OutputGenerator:
    """Generate specialized outputs for different tools."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.notebooklm_dir = base_dir / "ab_tools_NotebookLM"
        self.chatgpt_dir = base_dir / "ab_tools_ChatGPT"
        self.timeline_generator = TimelineGenerator()
        
        # Ensure output directories exist
        for tool_dir in [self.notebooklm_dir, self.chatgpt_dir]:
            (tool_dir / "outputs").mkdir(parents=True, exist_ok=True)
            (tool_dir / "pdfs").mkdir(parents=True, exist_ok=True)
    
    def generate_notebooklm_outputs(self, data, source_file):
        """Generate NotebookLM-specific output files."""
        output_dir = self.notebooklm_dir / "outputs"
        
        # Generate timeline
        timeline = self.timeline_generator.generate_notebooklm_timeline(
            data['messages'], 
            source_file
        )
        with open(output_dir / "timeline_analysis.txt", 'w', encoding='utf-8') as f:
            f.write(timeline)
            
        # Communication patterns will be handled separately...
        # Add other NotebookLM outputs...
    
    def generate_llm_outputs(self, data, source_file):
        """Generate LLM-optimized output files."""
        output_dir = self.chatgpt_dir / "outputs"
        
        # Generate timeline
        timeline = self.timeline_generator.generate_llm_timeline(
            data['messages'],
            source_file
        )
        with open(output_dir / "structured_timeline.txt", 'w', encoding='utf-8') as f:
            f.write(timeline)
            
        # Pattern analysis will be handled separately...
        # Add other LLM outputs...