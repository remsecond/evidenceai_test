import shutil
import tarfile
from pathlib import Path
import json
from datetime import datetime
import logging

class BackupManager:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.backup_dir = self.base_dir / 'backups'
        self.archive_dir = self.base_dir / 'archives'
        self.setup_logging()
        
    def setup_logging(self):
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / 'backup.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def create_backup(self, include_inputs=True):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'backup_{timestamp}'
        backup_path.mkdir(parents=True)
        
        # Track what's being backed up
        manifest = {
            'timestamp': timestamp,
            'includes_inputs': include_inputs,
            'contents': []
        }
        
        # Backup outputs
        output_backup = backup_path / 'output'
        if (self.base_dir / 'output').exists():
            shutil.copytree(self.base_dir / 'output', output_backup)
            manifest['contents'].append('output')
            
        # Backup inputs if requested
        if include_inputs and (self.base_dir / 'input').exists():
            input_backup = backup_path / 'input'
            shutil.copytree(self.base_dir / 'input', input_backup)
            manifest['contents'].append('input')
            
        # Backup logs
        log_backup = backup_path / 'logs'
        if (self.base_dir / 'logs').exists():
            shutil.copytree(self.base_dir / 'logs', log_backup)
            manifest['contents'].append('logs')
            
        # Save manifest
        with open(backup_path / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
            
        # Create compressed archive
        archive_name = f'backup_{timestamp}.tar.gz'
        with tarfile.open(self.backup_dir / archive_name, 'w:gz') as tar:
            tar.add(backup_path, arcname=backup_path.name)
            
        # Clean up uncompressed backup
        shutil.rmtree(backup_path)
        
        self.logger.info(f'Created backup: {archive_name}')
        return self.backup_dir / archive_name

    def restore_backup(self, backup_path):
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f'Backup not found: {backup_path}')
            
        # Extract archive
        temp_dir = self.backup_dir / 'temp_restore'
        temp_dir.mkdir(exist_ok=True)
        
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
            
        # Read manifest
        backup_contents = next(temp_dir.iterdir())
        with open(backup_contents / 'manifest.json') as f:
            manifest = json.load(f)
            
        # Restore contents
        for content_type in manifest['contents']:
            source = backup_contents / content_type
            target = self.base_dir / content_type
            
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            
        # Clean up
        shutil.rmtree(temp_dir)
        self.logger.info(f'Restored backup: {backup_path.name}')

    def list_backups(self):
        backups = []
        for backup in self.backup_dir.glob('backup_*.tar.gz'):
            try:
                with tarfile.open(backup, 'r:gz') as tar:
                    manifest_info = tar.getmember(f"{backup.stem}/manifest.json")
                    manifest_file = tar.extractfile(manifest_info)
                    manifest = json.load(manifest_file)
                    
                backups.append({
                    'file': backup.name,
                    'timestamp': manifest['timestamp'],
                    'includes_inputs': manifest['includes_inputs'],
                    'contents': manifest['contents']
                })
            except Exception as e:
                self.logger.error(f'Error reading backup {backup}: {str(e)}')
                
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    def archive_session(self, session_dir):
        session_dir = Path(session_dir)
        if not session_dir.exists():
            raise FileNotFoundError(f'Session not found: {session_dir}')
            
        # Create archive
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f'session_{session_dir.name}_{timestamp}.tar.gz'
        
        with tarfile.open(self.archive_dir / archive_name, 'w:gz') as tar:
            tar.add(session_dir, arcname=session_dir.name)
            
        self.logger.info(f'Archived session: {archive_name}')
        return self.archive_dir / archive_name

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=int, required=True)
    parser.add_argument('--backup', type=str, help='Backup to restore')
    parser.add_argument('--session', type=str, help='Session to archive')
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.mode == 1:  # Create backup
        backup_path = manager.create_backup()
        print(f'Created backup: {backup_path}')
    
    elif args.mode == 2:  # Restore backup
        if args.backup:
            manager.restore_backup(args.backup)
            print('Backup restored successfully')
        else:
            backups = manager.list_backups()
            print('\nAvailable backups:')
            for backup in backups:
                print(f"- {backup['file']} ({backup['timestamp']})")
    
    elif args.mode == 3:  # Manage archives
        if args.session:
            archive_path = manager.archive_session(args.session)
            print(f'Session archived: {archive_path}')
        else:
            print('\nArchived sessions:')
            for archive in manager.archive_dir.glob('session_*.tar.gz'):
                print(f'- {archive.name}')

if __name__ == '__main__':
    main()