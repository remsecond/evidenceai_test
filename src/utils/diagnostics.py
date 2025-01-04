import sys
import pkg_resources
import logging
import psutil
from pathlib import Path
import json

class SystemDiagnostics:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.setup_logging()
        
    def setup_logging(self):
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / 'diagnostics.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_system_resources(self):
        return {
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage(self.base_dir).total,
                'free': psutil.disk_usage(self.base_dir).free,
                'percent': psutil.disk_usage(self.base_dir).percent
            },
            'cpu_percent': psutil.cpu_percent()
        }

    def check_dependencies(self):
        required = {
            'PyPDF2': '3.0.0',
            'pandas': '1.5.0',
            'numpy': '1.21.0'
        }
        
        status = {pkg: {'installed': False, 'version': None} for pkg in required}
        
        for package, min_version in required.items():
            try:
                version = pkg_resources.get_distribution(package).version
                status[package] = {
                    'installed': True,
                    'version': version,
                    'meets_min': pkg_resources.parse_version(version) >= pkg_resources.parse_version(min_version)
                }
            except pkg_resources.DistributionNotFound:
                pass
                
        return status

    def validate_directory_structure(self):
        required_dirs = [
            'input',
            'output',
            'logs',
            'backups',
            'src/processors',
            'src/analyzers',
            'src/generators',
            'src/utils'
        ]
        
        structure = {}
        for dir_path in required_dirs:
            path = self.base_dir / dir_path
            structure[dir_path] = {
                'exists': path.exists(),
                'is_dir': path.is_dir() if path.exists() else False,
                'writeable': os.access(path, os.W_OK) if path.exists() else False
            }
        return structure

    def check_pipeline_components(self):
        required_files = [
            'src/processors/doc_processor.py',
            'src/analyzers/thread_analyzer.py',
            'src/analyzers/pattern_detector.py',
            'src/generators/timeline_generator.py',
            'src/generators/report_generator.py'
        ]
        
        components = {}
        for file_path in required_files:
            path = self.base_dir / file_path
            components[file_path] = {
                'exists': path.exists(),
                'size': path.stat().st_size if path.exists() else None,
                'modified': datetime.fromtimestamp(path.stat().st_mtime) if path.exists() else None
            }
        return components

    def run_full_diagnostics(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'system_resources': self.check_system_resources(),
            'dependencies': self.check_dependencies(),
            'directory_structure': self.validate_directory_structure(),
            'pipeline_components': self.check_pipeline_components()
        }

    def log_issues(self, diagnostics):
        issues = []
        
        # Check system resources
        if diagnostics['system_resources']['memory']['percent'] > 90:
            issues.append('Critical: High memory usage')
        if diagnostics['system_resources']['disk']['percent'] > 90:
            issues.append('Critical: Low disk space')
            
        # Check dependencies
        for pkg, status in diagnostics['dependencies'].items():
            if not status['installed']:
                issues.append(f'Error: Missing dependency {pkg}')
            elif not status.get('meets_min', True):
                issues.append(f'Warning: Outdated dependency {pkg}')
                
        # Check directory structure
        for dir_path, status in diagnostics['directory_structure'].items():
            if not status['exists']:
                issues.append(f'Error: Missing directory {dir_path}')
            elif not status['writeable']:
                issues.append(f'Error: Directory not writeable {dir_path}')
                
        # Check pipeline components
        for component, status in diagnostics['pipeline_components'].items():
            if not status['exists']:
                issues.append(f'Error: Missing pipeline component {component}')
                
        for issue in issues:
            self.logger.error(issue)
            
        return issues

def main():
    diagnostics = SystemDiagnostics()
    results = diagnostics.run_full_diagnostics()
    issues = diagnostics.log_issues(results)
    
    print("\nDiagnostics Results:")
    print("-" * 50)
    
    if not issues:
        print("✓ All systems operational")
    else:
        print("! Issues found:")
        for issue in issues:
            print(f"  - {issue}")
            
    # Save detailed results
    output_dir = diagnostics.base_dir / 'output'
    with open(output_dir / f'diagnostics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()