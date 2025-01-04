import sys
import pkg_resources
from pathlib import Path

def check_python_version():
    return sys.version_info >= (3, 8)

def check_dependencies():
    required = {
        'PyPDF2': '3.0.0',
        'pandas': '1.5.0',
        'numpy': '1.21.0'
    }
    
    missing = []
    outdated = []
    
    for package, min_version in required.items():
        try:
            version = pkg_resources.get_distribution(package).version
            if pkg_resources.parse_version(version) < pkg_resources.parse_version(min_version):
                outdated.append((package, version, min_version))
        except pkg_resources.DistributionNotFound:
            missing.append(package)
            
    return missing, outdated

def check_directories():
    base_dir = Path(__file__).parent.parent.parent
    required_dirs = [
        base_dir / 'input',
        base_dir / 'output',
        base_dir / 'src/processors',
        base_dir / 'src/analyzers',
        base_dir / 'src/generators',
        base_dir / 'src/utils'
    ]
    
    missing_dirs = [str(d) for d in required_dirs if not d.exists()]
    return missing_dirs

def validate_system():
    status = {
        'python_version': check_python_version(),
        'dependencies': check_dependencies(),
        'directories': check_directories()
    }
    return status

def main():
    status = validate_system()
    
    print("\nSystem Validation Report")
    print("=======================")
    
    # Python version
    print(f"\nPython Version: {'✓' if status['python_version'] else '✗'} {sys.version}")
    
    # Dependencies
    missing, outdated = status['dependencies']
    if not missing and not outdated:
        print("\nDependencies: ✓ All required packages installed and up to date")
    else:
        if missing:
            print("\nMissing Packages:")
            for package in missing:
                print(f"  • {package}")
        if outdated:
            print("\nOutdated Packages:")
            for package, current, required in outdated:
                print(f"  • {package}: {current} (requires >= {required})")
                
    # Directories
    missing_dirs = status['directories']
    if not missing_dirs:
        print("\nDirectories: ✓ All required directories present")
    else:
        print("\nMissing Directories:")
        for directory in missing_dirs:
            print(f"  • {directory}")
            
    print("\nValidation complete.")
    
    return all([
        status['python_version'],
        not status['dependencies'][0],
        not status['dependencies'][1],
        not status['directories']
    ])

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)