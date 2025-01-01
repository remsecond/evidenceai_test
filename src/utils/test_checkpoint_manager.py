import sys
from pathlib import Path
from datetime import datetime
import json
import shutil

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.checkpoint_manager import CheckpointManager

def test_checkpoint_manager():
    """Test all checkpoint manager functionality"""
    
    # Setup test environment
    test_dir = Path(__file__).parent.parent.parent / "test_checkpoints"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    manager = CheckpointManager(test_dir)
    
    # Test basic checkpoint creation
    print("\nTesting basic checkpoint creation...")
    test_data = {'test': 'data', 'number': 42}
    
    checkpoint_file = manager.save_checkpoint(
        'test_stage',
        test_data,
        {'test_meta': 'metadata'}
    )
    
    print(f"Created checkpoint: {checkpoint_file}")
    
    # Test checkpoint loading
    print("\nTesting checkpoint loading...")
    loaded = manager.load_checkpoint('test_stage')
    assert loaded['data'] == test_data, "Data mismatch!"
    print("Checkpoint loaded successfully")
    
    # Test checkpoint chain
    print("\nTesting checkpoint chain...")
    for i in range(3):
        test_data['number'] += 1
        manager.save_checkpoint('test_stage', test_data)
        
    chain = manager.get_chain_of_checkpoints('test_stage')
    print(f"Chain length: {len(chain)}")
    assert len(chain) == 4, "Chain length incorrect!"
    
    # Test checkpoint verification
    print("\nTesting checkpoint verification...")
    valid, invalid = manager.verify_all_checkpoints()
    print(f"Valid checkpoints: {len(valid)}")
    print(f"Invalid checkpoints: {len(invalid)}")
    
    # Test rollback
    print("\nTesting rollback...")
    second_checkpoint = chain[1]
    success = manager.rollback_to_checkpoint(second_checkpoint['checkpoint_id'])
    assert success, "Rollback failed!"
    
    current = manager.load_checkpoint('test_stage')
    assert current['data']['number'] == chain[1]['data']['number'], "Rollback data mismatch!"
    print("Rollback successful")
    
    # Test stage status
    print("\nTesting stage status...")
    status = manager.get_stage_status('test_stage')
    print(json.dumps(status, indent=2))
    
    # Test pruning
    print("\nTesting checkpoint pruning...")
    manager.prune_old_checkpoints(max_per_stage=2)
    remaining = list(manager.checkpoint_dir.glob("*.json"))
    print(f"Remaining checkpoints: {len(remaining)}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_checkpoint_manager()