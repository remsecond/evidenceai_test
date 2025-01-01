import os
import sys
from pathlib import Path
from datetime import datetime
import json
import shutil
from utils.session_validator import SessionValidator

class SessionError(Exception):
    """Custom exception for session errors"""
    pass

def check_environment():
    """Check required packages"""
    required_packages = ['PyPDF2', 'pandas', 'numpy']
    missing_packages = []
    
    print("Checking environment...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    return len(missing_packages) == 0

def load_project_status():
    """Load current project status"""
    base_dir = Path(__file__).parent.parent
    checkpoints_dir = base_dir / "output" / "checkpoints"
    session_file = base_dir / "output" / "current_session.txt"
    
    # Ensure output directory exists
    if not (base_dir / "output").exists():
        (base_dir / "output").mkdir(parents=True)
    
    status = {
        'modules': {
            'parsing': 'in_progress',
            'threading': 'pending',
            'relationship_analysis': 'pending',
            'topic_detection': 'pending'
        },
        'last_checkpoint': None,
        'current_stage': None
    }
    
    # Check for checkpoints
    if checkpoints_dir.exists():
        checkpoints = list(checkpoints_dir.glob("*.json"))
        if checkpoints:
            latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
            status['last_checkpoint'] = latest.name
            status['current_stage'] = latest.name.split('_')[0]
    
    # Save current session info
    with open(session_file, 'w') as f:
        f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Last checkpoint: {status['last_checkpoint']}\n")
        f.write(f"Current stage: {status['current_stage']}\n")
    
    print(f"Session info saved to: {session_file}")
    
    return status

def display_module_status(status):
    """Display module implementation status"""
    print("Module Implementation Status:")
    for module, state in status['modules'].items():
        print(f"- {module}: {state}")

def cleanup_environment(silent=False):
    """Clean up the development environment"""
    base_dir = Path(__file__).parent.parent
    
    if not silent:
        print("\n=== Cleanup Options ===")
        print("1. Clean output directory (preserve checkpoints)")
        print("2. Clean everything (including checkpoints)")
        print("3. Clean cache only")
        print("4. Cancel cleanup")
        
        choice = input("\nEnter choice (1-4): ")
    else:
        # For automated cleanup, use option 1 (clean but preserve checkpoints)
        choice = "1"
    
    if choice == "4":
        print("Cleanup cancelled")
        return False
        
    try:
        # Clean cache files
        if choice in ["1", "2", "3"]:
            if not silent:
                print("\nCleaning cache files...")
            cache_dirs = [
                base_dir / "src" / "__pycache__",
                base_dir / "src" / "processors" / "__pycache__",
                base_dir / "src" / "parsers" / "__pycache__",
                base_dir / "src" / "threader" / "__pycache__",
                base_dir / "src" / "analyzers" / "__pycache__",
                base_dir / "src" / "utils" / "__pycache__"
            ]
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                    if not silent:
                        print(f"✓ Cleaned {cache_dir}")
        
        # Clean output directory
        if choice in ["1", "2"]:
            output_dir = base_dir / "output"
            if output_dir.exists():
                if not silent:
                    print("\nCleaning output directory...")
                # Remove everything except checkpoints
                if choice == "1":
                    for item in output_dir.iterdir():
                        if item.name != "checkpoints":
                            if item.is_file():
                                item.unlink()
                            else:
                                shutil.rmtree(item)
                            if not silent:
                                print(f"✓ Removed {item}")
                # Remove everything including checkpoints
                else:
                    shutil.rmtree(output_dir)
                    if not silent:
                        print("✓ Cleaned entire output directory")
        
        if not silent:
            print("\nCleanup completed successfully")
        
    except Exception as e:
        if not silent:
            print(f"\nError during cleanup: {str(e)}")
        return False
    
    return True

def start_new_session():
    """Start a new session with validation and error recovery"""
    print("\n=== Starting New Session ===")
    validator = SessionValidator()
    
    try:
        # Step 1: Clean Environment
        print("\nStep 1: Cleaning environment...")
        if not cleanup_environment(silent=True):
            raise SessionError("Failed to clean environment")
            
        # Validate clean environment
        is_clean, clean_results = validator.validate_clean_environment()
        if not is_clean:
            print("\nEnvironment validation failed:")
            for issue in clean_results['issues']:
                print(f"❌ {issue}")
            for warning in clean_results['warnings']:
                print(f"⚠️ {warning}")
            
            retry = input("\nRetry cleanup? (y/n): ")
            if retry.lower() == 'y':
                if not cleanup_environment(silent=True):
                    raise SessionError("Failed to clean environment on retry")
            else:
                raise SessionError("Environment validation failed")
        
        print("✓ Environment cleaned and validated")
        
        # Step 2: Start Analysis Pipeline
        print("\nStep 2: Running analysis pipeline...")
        result = os.system("python src/test_pipeline.py")
        if result != 0:
            raise SessionError("Analysis pipeline failed")
            
        # Validate analysis results
        is_valid, analysis_results = validator.validate_analysis_results()
        if not is_valid:
            print("\nAnalysis validation failed:")
            for issue in analysis_results['issues']:
                print(f"❌ {issue}")
            for warning in analysis_results['warnings']:
                print(f"⚠️ {warning}")
            
            retry = input("\nRetry analysis? (y/n): ")
            if retry.lower() == 'y':
                result = os.system("python src/test_pipeline.py")
                if result != 0:
                    raise SessionError("Analysis pipeline failed on retry")
                is_valid, analysis_results = validator.validate_analysis_results()
                if not is_valid:
                    raise SessionError("Analysis validation failed after retry")
            else:
                raise SessionError("Analysis validation failed")
                
        print("✓ Analysis complete and validated")
        
        # Step 3: Generate New Session Prompt
        print("\nStep 3: Generating session prompt...")
        result = os.system("python src/generate_session_prompt.py")
        if result != 0:
            raise SessionError("Failed to generate session prompt")
            
        # Validate prompt
        is_valid, prompt_results = validator.validate_session_prompt()
        if not is_valid:
            print("\nPrompt validation failed:")
            for issue in prompt_results['issues']:
                print(f"❌ {issue}")
            for warning in prompt_results['warnings']:
                print(f"⚠️ {warning}")
            
            retry = input("\nRetry prompt generation? (y/n): ")
            if retry.lower() == 'y':
                result = os.system("python src/generate_session_prompt.py")
                if result != 0:
                    raise SessionError("Failed to generate session prompt on retry")
                is_valid, prompt_results = validator.validate_session_prompt()
                if not is_valid:
                    raise SessionError("Prompt validation failed after retry")
            else:
                raise SessionError("Prompt validation failed")
                
        print("✓ Session prompt generated and validated")
        
        # Final validation
        validation_results = validator.validate_full_session()
        if not validation_results['is_valid']:
            print("\nWarning: Some validation checks failed")
            print("Review the validation report for details:")
            print(json.dumps(validation_results, indent=2))
        
        print("\nNew session initialized successfully!")
        return True
        
    except SessionError as e:
        print(f"\nSession initialization failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return False

def main():
    print("\nStarting EvidenceAI Development Session...")
    print("Checking environment...")
    
    if not check_environment():
        print("\nError: Missing required packages. Please install missing packages.")
        sys.exit(1)
    
    print("\n=== Loading Project Status ===")
    status = load_project_status()
    display_module_status(status)
    
    print("\n=== Session Options ===")
    print("1. Start New Session (Clean + Analyze + Generate Prompt)")
    print("2. View Project Status Only")
    print("3. Start Analysis Pipeline")
    print("4. Clean Environment")
    print("5. Exit")
    
    while True:
        try:
            choice = input("Enter choice (1-5): ")
            if choice == "1":
                start_new_session()
                break
            elif choice == "2":
                # Just display status (already shown)
                print("\nStatus display complete")
                break
            elif choice == "3":
                # Start pipeline
                print("\nStarting analysis pipeline...")
                os.system("python src/test_pipeline.py")
                print("\nPipeline execution complete")
                break
            elif choice == "4":
                # Clean environment
                cleanup_environment()
                break
            elif choice == "5":
                print("\nExiting session...")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1-5.")
        except KeyboardInterrupt:
            print("\nSession interrupted")
            break
    
    input("\nPress any key to exit...")

if __name__ == "__main__":
    main()