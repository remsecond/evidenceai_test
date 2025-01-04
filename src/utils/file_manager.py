import argparse
import shutil
from pathlib import Path
import json
import logging
from datetime import datetime

class FileManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.input_dir = self.base_dir / 'input'
        self.output_dir = self.base_dir / 'output'
        self.archive_dir = self.base_dir / 'archives'
        
        # Set up logging
        logging.basicConfig(
            filename=self.base_dir / 'logs' / 'files.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def search_files(self, pattern=None):
        """Search for files matching pattern"""
        results = []
        
        # Search input directory
        for file in self.input_dir.rglob(pattern or '*'):
            if file.is_file():
                results.append({
                    'path': file,
                    'type': 'input',
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime)
                })
                
        # Search output directory
        for file in self.output_dir.rglob(pattern or '*'):
            if file.is_file():
                results.append({
                    'path': file,
                    'type': 'output',
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime)
                })
                
        return results
        
    def clean_directories(self, older_than=None):
        """Clean temporary and old files"""
        cleaned = []
        
        # Clean temp files
        for temp in self.output_dir.rglob('*.tmp'):
            temp.unlink()
            cleaned.append(str(temp))
            
        # Clean old files if specified
        if older_than:
            cutoff = datetime.now().timestamp() - (older_than * 86400)
            for old in self.output_dir.rglob('*'):
                if old.is_file() and old.stat().st_mtime < cutoff:
                    old.unlink()
                    cleaned.append(str(old))
                    
        return cleaned
        
    def get_file_details(self, filepath):
        """Get detailed file information"""
        path = Path(filepath)
        if not path.exists():
            return None
            
        stats = path.stat()
        return {
            'name': path.name,
            'path': str(path),
            'size': stats.st_size,
            'created': datetime.fromtimestamp(stats.st_ctime),
            'modified': datetime.fromtimestamp(stats.st_mtime),
            'type': path.suffix,
            'is_temp': path.suffix == '.tmp',
            'directory': str(path.parent)
        }
        
    def archive_files(self, files, archive_name=None):
        """Archive specified files"""
        if not archive_name:
            archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        archive_dir = self.archive_dir / archive_name
        archive_dir.mkdir(parents=True)
        
        archived = []
        for file in files:
            dest = archive_dir / Path(file).name
            shutil.copy2(file, dest)
            archived.append(str(dest))
            
        return archive_dir, archived

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=int, required=True)
    parser.add_argument('--pattern', type=str, help='Search pattern')
    parser.add_argument('--days', type=int, help='Days threshold for cleaning')
    args = parser.parse_args()
    
    manager = FileManager()
    
    if args.mode == 1:  # Search
        results = manager.search_files(args.pattern)
        print("\nSearch Results:")
        for result in results:
            print(f"- {result['path']}: {result['size']} bytes ({result['type']})")
            
    elif args.mode == 2:  # Clean
        cleaned = manager.clean_directories(args.days)
        print("\nCleaned Files:")
        for file in cleaned:
            print(f"- {file}")
            
    elif args.mode == 3:  # Details
        if args.pattern:
            details = manager.get_file_details(args.pattern)
            if details:
                print("\nFile Details:")
                for key, value in details.items():
                    print(f"{key}: {value}")
            else:
                print("File not found")
                
if __name__ == '__main__':
    main()