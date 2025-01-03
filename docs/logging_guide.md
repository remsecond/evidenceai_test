# EvidenceAI Logging System Guide

## Overview
The EvidenceAI logging system provides comprehensive tracking of all operations, errors, and progress through the analysis pipeline. The system is designed for debugging, auditing, and process verification.

## Log Structure

### Main Log File
Location: `output/analysis.log`

Format:
```
2024-01-02 10:15:23,456 - analyzer_name - INFO - Operation description
```

Components:
- Timestamp: ISO format with milliseconds
- Module: Source of the log entry
- Level: INFO/WARNING/ERROR
- Message: Detailed description

### Log Levels
- INFO: Normal operations and progress updates
- WARNING: Non-critical issues that don't stop processing
- ERROR: Critical issues that halt or impact results

## Checkpoint System

### Location
`output/checkpoints/`

### Naming Convention
`{stage}_{timestamp}.json`
Example: `pdf_parsing_20240102_101523.json`

### Checkpoint Contents
```json
{
    "status": "success|error",
    "timestamp": "2024-01-02T10:15:23.456",
    "metadata": {
        "stage_info": "...",
        "processing_stats": "..."
    },
    "data": {
        // Stage-specific results
    }
}
```

## Key Operations Logged

### Pipeline Initialization
```
INFO - Pipeline initialized with input directory: {path}
INFO - Found {count} PDF files to process
```

### PDF Parsing
```
INFO - Starting PDF parsing for: {filename}
INFO - Extracted {count} messages from PDF
```

### Message Analysis
```
INFO - Running message enrichment
INFO - Processed {count} message relationships
```

## Error Handling

### Error Format
```
ERROR - {operation}: {error_description}
TRACE - {stack_trace}
```

### Common Error Types
1. File Access Issues
2. PDF Parsing Errors
3. Data Processing Failures

## Using the Logs

### Monitoring Progress
1. Check `analysis.log` for stage completion
2. Review INFO messages for process flow
3. Monitor WARNING messages for potential issues

### Debugging
1. Check ERROR messages for failure points
2. Review surrounding INFO messages for context
3. Use timestamps to track operation sequence

### Audit Trail
- Each operation is logged with timestamp
- Checkpoints preserve state at each stage
- Error conditions are fully documented