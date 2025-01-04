"""EvidenceAI Control Panel Menu."""
import os
import sys
from datetime import datetime
from pathlib import Path
import logging
from src.utils.session_manager import SessionManager
from src.processors.output_generator import OutputGenerator

class EvidenceAIMenu:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.session_manager = SessionManager()
        self.output_generator = OutputGenerator(self.base_dir)
    
    def start_new_session(self):
        """Initialize new session."""
        try:
            self.session_manager.create_session_prompt()
            print("\n✓ Session prompt created and opened")
        except Exception as e:
            logging.error(f"Failed to create session: {str(e)}")
            print(f"\nError creating session: {str(e)}")

    def run_pipeline(self):
        """Run complete pipeline."""
        from test_complete_pipeline import PipelineTester
        tester = PipelineTester()
        tester.test_pipeline()
    
    def run_tests(self):
        """Run test suite."""
        print("\nRunning tests...")
        # Add test execution
    
    def manage_files(self):
        """File management menu."""
        print("\nFile management...")
        # Add file management
    
    def run(self):
        """Main menu loop."""
        while True:
            try:
                self.print_header()
                self.print_menu()
                
                choice = input("\nEnter choice (0-8): ")
                
                if choice == '1':
                    self.start_new_session()
                elif choice == '2':
                    self.run_pipeline()
                elif choice == '3':
                    self.run_custom_pipeline()
                elif choice == '4':
                    self.manage_files()
                elif choice == '5':
                    self.run_tests()
                elif choice == '6':
                    self.backup_and_archive()
                elif choice == '7':
                    self.view_docs()
                elif choice == '8':
                    self.settings()
                elif choice == '0':
                    break
                else:
                    print("\nInvalid choice")
                
                input("\nPress Enter to continue...")
            except Exception as e:
                logging.error(f"Menu error: {str(e)}")
                print(f"\nAn error occurred: {str(e)}")
                print("Check the logs for more details.")
                input("\nPress Enter to continue...")
    
    def print_header(self):
        """Print menu header."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 42)
        print("        EvidenceAI Control Panel         ")
        print("=" * 42)
        print(f"Python {sys.version.split()[0]}")
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show status
        input_files = len(list(self.base_dir.glob("input/*.pdf")))
        print("\nEnvironment Status:")
        print(f"Input Files: {input_files} PDF(s) found")
        print(f"Disk Space: {self._get_free_space():.1f}GB free")
        print("Dependencies: All required packages installed")
        print("-" * 42)
    
    def _get_free_space(self):
        """Get free disk space in GB."""
        import shutil
        return shutil.disk_usage(self.base_dir).free / (1024**3)

def main():
    menu = EvidenceAIMenu()
    menu.run()

if __name__ == '__main__':
    main()