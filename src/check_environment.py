def check_environment():
    """Check if all required packages are installed"""
    required_packages = {
        'PyPDF2': 'PyPDF2',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    missing = []
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(install_name)
            print(f"✗ {package}")
            
    if missing:
        print("\nMissing required packages. Please run:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

if __name__ == "__main__":
    print("Checking environment...")
    check_environment()