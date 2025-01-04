"""Configuration settings for EvidenceAI pipeline."""
from pathlib import Path
import json

class PipelineConfig:
    """Manage pipeline configuration."""
    
    DEFAULT_CONFIG = {
        "output_format": "TXT",  # or "PDF"
        "batch_processing": True,
        "save_raw_json": True,
        "analysis_types": {
            "timeline": True,
            "patterns": True,
            "participants": True,
            "keywords": True,
            "response_times": True
        },
        "error_handling": {
            "continue_on_error": True,
            "save_error_log": True
        },
        "output_structure": {
            "notebooklm": {
                "include_metadata": True,
                "split_files": True,
                "file_types": [
                    "timeline_analysis",
                    "communication_patterns",
                    "thread_analysis",
                    "participant_interactions",
                    "statistical_summary",
                    "key_terms"
                ]
            },
            "llm": {
                "include_context": True,
                "file_types": [
                    "structured_timeline",
                    "pattern_analysis",
                    "analysis_prompts"
                ]
            }
        }
    }
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config_file = base_dir / "config" / "pipeline_config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Save default config
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set configuration value."""
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self.save_config()
    
    def get_output_format(self):
        """Get current output format."""
        return self.get('output_format', 'TXT')
    
    def set_output_format(self, format_type):
        """Set output format (TXT or PDF)."""
        if format_type not in ['TXT', 'PDF']:
            raise ValueError("Output format must be 'TXT' or 'PDF'")
        self.set('output_format', format_type)
    
    def get_enabled_analyses(self):
        """Get list of enabled analysis types."""
        analysis_types = self.get('analysis_types', {})
        return [name for name, enabled in analysis_types.items() if enabled]
    
    def get_notebooklm_files(self):
        """Get list of enabled NotebookLM output files."""
        return self.get('output_structure.notebooklm.file_types', [])
    
    def get_llm_files(self):
        """Get list of enabled LLM output files."""
        return self.get('output_structure.llm.file_types', [])