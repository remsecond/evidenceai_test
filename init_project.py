from pathlib import Path
import logging

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def init_project():
    """Initialize project directory structure"""
    logger = setup_logging()
    base_dir = Path(__file__).parent
    
    # Define all required directories
    directories = [
        # Input directories
        'input',
        
        # Output directories
        'output/json/messages',
        'output/json/threads',
        'output/json/analysis',
        'output/text/notebooks',
        'output/text/summaries',
        
        # Source code directories
        'src/parsers',
        'src/analyzers',
        'src/utils',
        
        # Test directories
        'tests/test_input',
        'tests/test_output',
        
        # Coverage report directory
        'coverage_report'
    ]
    
    # Create all directories
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Verified directory: {dir_path}")

    # Create empty __init__.py files in Python package directories
    python_packages = [
        'src',
        'src/parsers',
        'src/analyzers',
        'src/utils'
    ]
    
    for package in python_packages:
        init_file = base_dir / package / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            logger.info(f"Created __init__.py in {package}")
    
    logger.info("\nProject structure initialized successfully!")
    
    # Return the structure for verification
    return {
        'base_dir': base_dir,
        'directories': directories,
        'python_packages': python_packages
    }

def verify_structure(structure):
    """Verify all directories and files exist"""
    logger = logging.getLogger(__name__)
    base_dir = structure['base_dir']
    
    # Check directories
    missing_dirs = []
    for dir_path in structure['directories']:
        full_path = base_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    # Check __init__.py files
    missing_inits = []
    for package in structure['python_packages']:
        init_file = base_dir / package / '__init__.py'
        if not init_file.exists():
            missing_inits.append(f"{package}/__init__.py")
    
    if missing_dirs or missing_inits:
        logger.error("Project structure verification failed!")
        if missing_dirs:
            logger.error("Missing directories: %s", ', '.join(missing_dirs))
        if missing_inits:
            logger.error("Missing __init__.py files: %s", ', '.join(missing_inits))
        return False
    
    logger.info("Project structure verified successfully!")
    return True

if __name__ == "__main__":
    structure = init_project()
    verify_structure(structure)