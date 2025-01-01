from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Tuple, Optional

class SessionValidator:
    """Validates session state and transitions"""
    
    REQUIRED_RESULT_KEYS = {
        'metadata': ['stage', 'timestamp', 'pipeline_version'],
        'validation': ['is_valid', 'checks_performed', 'warnings']
    }
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parents[2]
        self.output_dir = self.base_dir / "output"
        self.checkpoint_dir = self.output_dir / "checkpoints"
    
    def validate_clean_environment(self) -> Tuple[bool, Dict]:
        """Validate environment is properly cleaned"""
        issues = []
        warnings = []
        
        # Check output directory structure
        if not self.output_dir.exists():
            issues.append("Output directory missing")
        if not self.checkpoint_dir.exists():
            issues.append("Checkpoints directory missing")
            
        # Check for unexpected files
        if self.output_dir.exists():
            for item in self.output_dir.iterdir():
                if item.name != "checkpoints" and item.name != "current_session.txt":
                    warnings.append(f"Unexpected file in output: {item.name}")
        
        # Check for cache files
        cache_dirs = [
            self.base_dir / "src" / "__pycache__",
            self.base_dir / "src" / "processors" / "__pycache__",
            self.base_dir / "src" / "parsers" / "__pycache__",
            self.base_dir / "src" / "threader" / "__pycache__",
            self.base_dir / "src" / "analyzers" / "__pycache__",
            self.base_dir / "src" / "utils" / "__pycache__"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                warnings.append(f"Cache directory exists: {cache_dir}")
        
        is_valid = len(issues) == 0
        return is_valid, {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_analysis_results(self) -> Tuple[bool, Dict]:
        """Validate analysis results are present and valid"""
        issues = []
        warnings = []
        
        # Check for results file
        results_files = list(self.output_dir.glob("test_results_*.json"))
        if not results_files:
            issues.append("No analysis results found")
        else:
            latest_results = max(results_files, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest_results) as f:
                    results = json.load(f)
                    
                # Validate results structure
                self._validate_result_structure(results, issues, warnings)
                
                # Check stage completion
                expected_stages = {'parsing', 'threading', 'analysis'}
                found_stages = set(results.get('stages', {}).keys())
                missing_stages = expected_stages - found_stages
                if missing_stages:
                    issues.append(f"Missing stages: {', '.join(missing_stages)}")
                
                # Validate each stage
                for stage, stage_data in results.get('stages', {}).items():
                    self._validate_stage_results(stage, stage_data, issues, warnings)
                    
            except json.JSONDecodeError:
                issues.append("Results file is not valid JSON")
            except Exception as e:
                issues.append(f"Error reading results: {str(e)}")
        
        is_valid = len(issues) == 0
        return is_valid, {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_result_structure(self, results: Dict, issues: list, warnings: list) -> None:
        """Validate the structure of results"""
        # Check top-level keys
        required_keys = {'metadata', 'status', 'stages', 'validation'}
        missing_keys = required_keys - set(results.keys())
        if missing_keys:
            issues.append(f"Missing required keys: {', '.join(missing_keys)}")
            
        # Check metadata structure
        if 'metadata' in results:
            for key in self.REQUIRED_RESULT_KEYS['metadata']:
                if key not in results['metadata']:
                    issues.append(f"Missing metadata field: {key}")
                    
        # Check validation structure
        if 'validation' in results:
            for key in self.REQUIRED_RESULT_KEYS['validation']:
                if key not in results['validation']:
                    issues.append(f"Missing validation field: {key}")
    
    def _validate_stage_results(self, stage: str, data: Dict, issues: list, warnings: list) -> None:
        """Validate individual stage results"""
        if data.get('status') != 'success':
            issues.append(f"Stage {stage} failed with status: {data.get('status')}")
            
        if not data.get('validation', {}).get('is_valid'):
            warnings.append(f"Stage {stage} has validation warnings")
    
    def validate_session_prompt(self) -> Tuple[bool, Dict]:
        """Validate session prompt is generated and valid"""
        issues = []
        warnings = []
        
        # Check for prompt file
        prompt_files = list(self.base_dir.glob("SESSION_PROMPT_*.md"))
        if not prompt_files:
            issues.append("No session prompt found")
        else:
            latest_prompt = max(prompt_files, key=lambda p: p.stat().st_mtime)
            
            try:
                with open(latest_prompt) as f:
                    content = f.read()
                    
                # Check prompt content
                required_sections = [
                    "Project Status",
                    "Directory Structure",
                    "Pipeline Status",
                    "Current Focus",
                    "Session Start Instructions"
                ]
                
                for section in required_sections:
                    if section not in content:
                        issues.append(f"Missing required section in prompt: {section}")
                        
                # Check if prompt is recent
                if (datetime.now() - datetime.fromtimestamp(latest_prompt.stat().st_mtime)).seconds > 300:
                    warnings.append("Session prompt may be outdated")
                    
            except Exception as e:
                issues.append(f"Error reading prompt file: {str(e)}")
        
        is_valid = len(issues) == 0
        return is_valid, {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_full_session(self) -> Dict:
        """Run all validations and return comprehensive report"""
        env_valid, env_results = self.validate_clean_environment()
        analysis_valid, analysis_results = self.validate_analysis_results()
        prompt_valid, prompt_results = self.validate_session_prompt()
        
        return {
            'is_valid': all([env_valid, analysis_valid, prompt_valid]),
            'environment': env_results,
            'analysis': analysis_results,
            'prompt': prompt_results,
            'timestamp': datetime.now().isoformat()
        }