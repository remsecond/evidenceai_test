"""Create EvidenceAI session prompt."""
from datetime import datetime
from pathlib import Path

def create_session():
    base_dir = Path(__file__).parent
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    prompt_file = base_dir / f"SESSION_PROMPT_{timestamp}.md"
    
    content = f"""# EvidenceAI Development Session - {datetime.now().strftime('%B %d, %Y')}

## Project Status
PDF Files: {len(list(base_dir.glob('input/*.pdf')))} in input/
Last Output: {len(list(base_dir.glob('output/*.json')))} files

## Priority Tasks
1. Fix Report Generation
   - Timeline analysis (incomplete data)
   - Communication patterns (missing analysis)
   - Thread analysis (relationship mapping)
   - Participant interactions (interaction patterns)
   - Statistical summary (response metrics)

2. Tool Integration
   - NotebookLM format improvements
   - LLM prompt optimization
   - Data validation

3. Infrastructure
   - Pipeline reliability
   - Error handling
   - Progress tracking

## File Organization
```
evidenceai_test/
├── input/                    # Source PDFs
├── output/                   # Processing results
├── ab_tools_NotebookLM/     # NotebookLM outputs
└── ab_tools_ChatGPT/        # LLM outputs
```

## Next Steps
1. Fix timeline generation
2. Implement missing analyses
3. Validate formats
4. Test complete pipeline"""
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created session prompt: {prompt_file}")

if __name__ == '__main__':
    create_session()