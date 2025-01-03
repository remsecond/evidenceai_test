# EvidenceAI User Guide

## Introduction

EvidenceAI helps analyze Our Family Wizard (OFW) communications by extracting, organizing, and enriching message data while preserving context and relationships. The pipeline processes PDFs into structured data that can be analyzed by various AI tools.

## Running the Pipeline

### 1. Prepare Your Files
1. Export your OFW communications as PDF
2. Place the PDF in the `input/` directory
3. Verify file permissions

### 2. Start the Analysis
Option A: Using the Batch File
```bash
1. Double-click run_analysis.bat
2. Choose "Start Fresh" when prompted
3. Wait for completion message
```

Option B: Using Python Directly
```bash
1. Open command prompt
2. Navigate to project directory
3. Run: python src/run_analysis.py
```

### 3. Monitor Progress
- Watch the console for stage completion
- Check `output/analysis.log` for detailed progress
- Review checkpoints in `output/checkpoints/`

## Finding Analysis Products

### Directory Structure
```
output/
├── checkpoints/               # Stage results
│   ├── pdf_parsing_*.json    # Raw message data
│   ├── enrichment_*.json     # Enhanced messages
│   └── relationships_*.json  # Message connections
├── final/                    # Analysis outputs
└── analysis.log             # Process log
```

### Key Output Files

1. Message Data (JSON):
```json
{
    "metadata": {
        "total_messages": 123,
        "date_range": {...},
        "participants": {...}
    },
    "messages": [
        {
            "original": {...},
            "metadata": {...},
            "relationships": {...}
        }
    ]
}
```

2. Relationship Maps (JSON):
```json
{
    "temporal": {...},
    "reference": {...},
    "participant": {...}
}
```

## Using with AI Tools

### Preparing Data for Analysis

1. Message Content:
   - Use `final/messages.json` for content analysis
   - Reference `final/relationships.json` for context

2. Temporal Analysis:
   - Use `final/temporal_analysis.json` for timing patterns
   - Reference `metadata.date_range` for context

3. Relationship Analysis:
   - Use `final/interaction_maps.json` for communication patterns
   - Reference `metadata.participants` for context

### Example Analysis Approaches

1. Communication Pattern Analysis:
```python
# Example prompt structure
prompt = f"""
Analyze the communication patterns in this dataset focusing on:
1. Temporal patterns (when do exchanges occur?)
2. Response behaviors (how quickly do parties respond?)
3. Threading patterns (how do conversations develop?)

Data: {json_data}
"""
```

2. Relationship Mapping:
```python
# Example prompt structure
prompt = f"""
Map the relationships between participants considering:
1. Direct interactions (who talks to whom?)
2. Response patterns (who responds to whom?)
3. Communication style (how do interactions evolve?)

Data: {json_data}
"""
```

## Best Practices

### Data Handling
1. Always use complete checkpoint data
2. Preserve context from metadata
3. Reference original messages when needed

### Analysis Approaches
1. Start with broad patterns
2. Drill down into specific threads
3. Cross-reference relationships
4. Maintain objective perspective

### Remember
- Data is enriched but not interpreted
- Original context is preserved
- Multiple analysis perspectives are possible
- Results should be verified against raw data

## Troubleshooting

### Common Issues
1. Missing Files
   - Check input directory
   - Verify file permissions
   - Review analysis.log

2. Processing Errors
   - Check checkpoint files
   - Review error messages
   - Start fresh if needed

3. Analysis Issues
   - Verify data completeness
   - Check file formats
   - Review relationship maps

### Getting Help
1. Check logs for errors
2. Review checkpoint data
3. Verify file permissions
4. Consult documentation