import subprocess
import sys
from pathlib import Path
import logging
import pkg_resources

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_dependencies(logger):
    """Check if all required packages are installed"""
    requirements_path = Path(__file__).parent / 'requirements.txt'
    if not requirements_path.exists():
        logger.error("requirements.txt not found!")
        return False

    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    missing = []
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
        except pkg_resources.DistributionNotFound:
            missing.append(requirement.split('>=')[0])

    if missing:
        logger.error("Missing required packages: %s", ', '.join(missing))
        logger.info("Please run: pip install -r requirements.txt")
        return False
    return True

def check_directories(logger):
    """Ensure all required directories exist"""
    base_dir = Path(__file__).parent
    required_dirs = [
        'src/parsers',
        'src/analyzers',
        'tests/test_input',
        'tests/test_output'
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            logger.error(f"Required directory missing: {dir_path}")
            return False
    return True

def run_command(command, logger):
    """Run a command and log output"""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error:\n{e.stderr}")
        return False

def main():
    logger = setup_logging()
    base_dir = Path(__file__).parent
    success = True

    # Check environment
    logger.info("Checking environment...")
    if not check_dependencies(logger):
        return False
    if not check_directories(logger):
        return False

    # Generate test PDFs
    logger.info("Generating test PDFs...")
    if not run_command([sys.executable, 'tests/generate_test_pdfs.py'], logger):
        logger.error("Failed to generate test PDFs")
        return False

    # Run tests with coverage
    logger.info("Running tests with coverage...")
    test_command = [
        'pytest',
        'tests/',
        '-v',
        '--cov=src',
        '--cov-report=html:coverage_report',
        '--cov-report=term-missing'
    ]
    
    if not run_command(test_command, logger):
        logger.error("Tests failed")
        success = False

    # Report results
    if success:
        logger.info("All tests completed successfully!")
        logger.info("Coverage report generated in: coverage_report/index.html")
    else:
        logger.error("Some tests failed. Check logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()