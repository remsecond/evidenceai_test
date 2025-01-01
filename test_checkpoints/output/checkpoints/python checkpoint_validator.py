```json
{
    "checkpoints": {
        "cp_001": {
            "timestamp": "2024-01-20T10:30:00Z",
            "stage": "preprocessing",
            "status": "complete",
            "data_hash": "8a1f7d0e9b6c4a3d2f5e8b7a0c3d6f9e1b4a7c0d3f6e9b2a5c8d1f4e7b0a3",
            "metadata": {
                "files_processed": 10,
                "stage_duration": "00:05:30"
            }
        },
        "cp_002": {
            "timestamp": "2024-01-20T10:35:00Z",
            "stage": "analysis",
            "status": "complete",
            "data_hash": "7b2e8f1d9c4a5b6e3d2f1a8c7b4e9d6a3f0c5b2e8d7a4f1c6b3e9d2a5f8",
            "metadata": {
                "analysis_type": "basic",
                "patterns_found": 5
            }
        }
    },
    "latest_checkpoint": "cp_002"
}
```

Save this as `checkpoint_registry.json` in the same directory as the validation script and try running it again:

```bash
python checkpoint_validator.py
```