# EvidenceAI Analysis Pipeline

## Project Structure
```
evidenceai_test/
├── input/                # Original OFW PDFs
├── output/              
│   ├── checkpoints/     # Stage results
│   ├── analysis.log     # Process logging
│   └── final/           # Analysis outputs
├── src/
│   ├── parsers/         # PDF parsing modules
│   │   └── pdf_parser.py
│   └── analyzers/       # Analysis modules
│       ├── message_enricher.py
│       └── relationship_detector.py
└── docs/                # Documentation
    └── logging_guide.md
```

## Quick Start

1. Place OFW PDF in `input/` directory
2. Run the analysis:
   ```bash
   python src/run_analysis.py
   ```
   Or double-click `run_analysis.bat`

3. Choose execution mode:
   - "Start Fresh" for new analysis
   - "Continue" to resume from last checkpoint
   - "Exit" to cancel

4. Check outputs:
   - `output/checkpoints/` for stage results
   - `output/analysis.log` for process details
   - `output/final/` for completed analysis

## Current Capabilities

### 1. PDF Parsing (Implemented)
- Extracts messages from OFW PDFs
- Preserves all metadata
- Maintains message structure

### 2. Message Enrichment (Implemented)
- Adds objective metadata
- Maps temporal relationships
- Tracks participant information

### 3. Relationship Detection (Implemented)
- Identifies message connections
- Maps conversation threads
- Preserves context

## How It Works

### Data Flow
1. PDF → Raw Messages
   - Complete message extraction
   - Metadata preservation
   - Structure validation

2. Raw Messages → Enriched Data
   - Temporal markers
   - Participant mapping
   - Response tracking

3. Enriched Data → Relationships
   - Thread identification
   - Interaction mapping
   - Context preservation

### Checkpoint System
- Each stage saves progress
- Allows process resumption
- Preserves data integrity

### Logging System
- Detailed operation logging
- Error tracking
- Process verification
- See `docs/logging_guide.md` for details

## Error Handling

### Common Issues
1. PDF Access
   - Check file permissions
   - Verify PDF in input directory
   - Review analysis.log for details

2. Processing Errors
   - Check checkpoint files
   - Review error messages
   - Restart from last good checkpoint

3. Output Issues
   - Verify directory permissions
   - Check disk space
   - Review log for write errors

## Development Status

### Completed
- [x] PDF parsing engine
- [x] Message enrichment system
- [x] Relationship detection
- [x] Logging system
- [x] Checkpoint management

### In Progress
- [ ] Topic analysis
- [ ] Pattern visualization
- [ ] Timeline generation

### Planned
- [ ] Cross-document analysis
- [ ] Interactive visualizations
- [ ] Report generation

## Contributing
1. Review existing modules in `src/`
2. Follow logging guidelines
3. Maintain checkpoint compatibility
4. Document new features