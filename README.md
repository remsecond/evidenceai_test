# EvidenceAI Analysis Pipeline

## Project Structure
```
evidenceai_test/
├── input/                    # Raw OFW PDFs
├── output/                   # Analysis outputs
├── src/                      # Source code
│   ├── parsers/             # PDF and message parsing
│   ├── analyzers/           # Analysis modules
│   └── utils/               # Utility functions
├── tests/                   # Test files
└── notebooks/              # Jupyter notebooks for exploration
```

## Setup
1. Place OFW PDFs in `input/`
2. Run basic verification: `python src/verify_setup.py`
3. Run parser: `python src/run_parser.py`
4. Run analysis: `python src/run_analysis.py`

## Development Status
- [x] Basic PDF parsing
- [x] Message threading
- [x] Relationship analysis
- [x] Topic detection
- [ ] Enhanced threading
- [ ] Pattern visualization

## Picking Up Where We Left Off
1. All code is version controlled
2. Each analysis step saves intermediate results
3. Can restart from any checkpoint