"""Configuration management for EvidenceAI."""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages EvidenceAI configuration settings."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config_dir = base_dir / "config"
        self.config_file = self.config_dir / "default_config.json"
        self.user_config_file = self.config_dir / "user_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration, combining default and user settings."""
        # Load default config
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Override with user config if it exists
        if self.user_config_file.exists():
            with open(self.user_config_file, 'r') as f:
                user_config = json.load(f)
                config = self._deep_update(config, user_config)
        
        return config
    
    def _deep_update(self, d: Dict, u: Dict) -> Dict:
        """Recursively update nested dictionaries."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the correct nested level
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to user config if requested
        if save:
            self.save_user_config()
    
    def save_user_config(self) -> None:
        """Save current configuration to user config file."""
        with open(self.user_config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_directory(self, dir_type: str) -> Path:
        """Get full path for a configured directory."""
        dir_path = self.get(f'directories.{dir_type}')
        if dir_path:
            full_path = self.base_dir / dir_path
            full_path.mkdir(exist_ok=True)
            return full_path
        raise ValueError(f"Directory type '{dir_type}' not configured")
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.get(f'{feature}.enabled', False)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate current configuration."""
        errors = []
        
        # Check required directories
        for dir_type in self.get('directories', {}).keys():
            try:
                path = self.get_directory(dir_type)
                if not path.exists():
                    errors.append(f"Directory '{dir_type}' does not exist: {path}")
            except Exception as e:
                errors.append(f"Error with directory '{dir_type}': {str(e)}")
        
        # Check required pipeline stages
        for stage, config in self.get('pipeline.stages', {}).items():
            if config.get('required') and not config.get('enabled'):
                errors.append(f"Required pipeline stage '{stage}' is disabled")
        
        # Validate file types
        primary = self.get('file_types.primary')
        allowed = self.get('file_types.allowed', [])
        if primary and primary not in allowed:
            errors.append(f"Primary file type '{primary}' not in allowed types")
        
        return len(errors) == 0, errors

    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        if self.user_config_file.exists():
            os.remove(self.user_config_file)
        self.config = self._load_config()
    
    def print_config(self) -> None:
        """Print current configuration in a readable format."""
        def _print_dict(d: Dict, indent: int = 0):
            for k, v in d.items():
                if isinstance(v, dict):
                    print("  " * indent + f"{k}:")
                    _print_dict(v, indent + 1)
                else:
                    print("  " * indent + f"{k}: {v}")
        
        print("\nCurrent Configuration:")
        print("=====================")
        _print_dict(self.config)

def get_config(base_dir: Optional[Path] = None) -> ConfigManager:
    """Get configuration manager instance."""
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    return ConfigManager(base_dir)