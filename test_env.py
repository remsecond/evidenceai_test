import sys
from pathlib import Path

def test_environment():
    print("Testing EvidenceAI Environment")
    print("-" * 50)
    
    # Print current directory
    current_dir = Path.cwd()
    print(f"Current Directory: {current_dir}")
    
    # Check input directory
    input_dir = current_dir / "input"
    print(f"\nChecking input directory: {input_dir}")
    if input_dir.exists():
        print("✓ Input directory exists")
        # List files
        print("Files found:")
        for f in input_dir.glob("*"):
            print(f"  - {f.name}")
    else:
        print("✗ Input directory not found")
    
    # Check required modules
    print("\nChecking required modules:")
    required_modules = ['json', 'datetime', 'pathlib']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} available")
        except ImportError:
            print(f"✗ {module} missing")
    
    print("\nEnvironment test complete")

if __name__ == "__main__":
    test_environment()