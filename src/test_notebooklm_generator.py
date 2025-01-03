import os
from pathlib import Path
import json
from datetime import datetime, timedelta

class TestNotebookLMGenerator:
    """Generates test NotebookLM documents from OFW data"""
    
    def __init__(self):
        self.base_dir = Path("C:/Users/robmo/OneDrive/Documents/evidenceai_test")
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output" / "OFW_Messages_Report_Dec"
        self.notebooklm_dir = self.output_dir / "notebooklm_docs"

    def setup_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.input_dir, self.output_dir, self.notebooklm_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create subdirectories for different document types
        for subdir in ['threads', 'topics', 'participants']:
            (self.notebooklm_dir / subdir).mkdir(exist_ok=True)

    def generate_test_documents(self):
        """Generate test NotebookLM documents"""
        self.setup_directories()
        
        # Generate main documents
        self._generate_overview()
        self._generate_timeline()
        self._generate_cross_references()
        self._generate_index()
        
        # Generate thread documents
        self._generate_thread_documents()
        
        # Generate topic documents
        self._generate_topic_documents()
        
        # Generate participant documents
        self._generate_participant_documents()

    def _generate_overview(self):
        """Generate overview document"""
        overview = f"""# Communication Analysis - December 2024

## Overview
- Source File: OFW_Messages_Report_Dec.pdf
- Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
- Message Count: 287
- Primary Participants: 2
- Key Topics: ["scheduling", "finance", "property", "children"]

## Communication Summary
- Active Scheduling Discussion
- Financial Coordination
- Property-Related Planning
- Children's Activities & School

## Document Organization
1. [Timeline Analysis](timeline.md) - Chronological view of communications
2. [Cross References](cross_references.md) - Related topics and threads
3. [Thread Analysis](threads/) - Individual conversation threads
4. [Topic Analysis](topics/) - Subject matter deep dives
5. [Participant Analysis](participants/) - Individual communication patterns

## Key Discussion Areas
1. Schedule Coordination
   - Visitation Planning
   - Activity Scheduling
   - Holiday Arrangements

2. Financial Coordination
   - Expense Sharing
   - Payment Tracking
   - Property Costs

3. Children's Activities
   - School Matters
   - Sports/Recreation
   - Healthcare

4. Property Matters
   - Maintenance
   - Future Planning
   - Shared Responsibilities

## Search Tips
- Use dates for timeline searches (e.g., "December 5th")
- Reference specific topics (e.g., "schedule", "finance")
- Include participant names for filtering
- Cross-reference between documents using provided links

## Next Steps
1. Review [Timeline](timeline.md) for chronological context
2. Explore [Cross References](cross_references.md) for relationships
3. Deep dive into specific [Threads](threads/) or [Topics](topics/)
4. Analyze [Participant](participants/) communication patterns
"""
        with open(self.notebooklm_dir / "00_Overview.md", 'w', encoding='utf-8') as f:
            f.write(overview)

    def _generate_timeline(self):
        """Generate timeline document"""
        timeline = """# Communication Timeline Analysis

## December 2024 Timeline

### Week 1 (Dec 1-7)
- Initial schedule discussions
- Financial planning and coordination
- Property-related communications
- Children's activity organization

### Week 2 (Dec 8-14)
- Schedule refinements
- Expense tracking and sharing
- Activity coordination
- Property discussions

### Week 3 (Dec 15-21)
- Holiday planning
- Financial reconciliation
- School-related coordination
- Sports and activities

### Week 4 (Dec 22-31)
- Holiday schedule execution
- Year-end financial matters
- Activity coordination
- Future planning

## Communication Patterns
- Regular morning updates
- Prompt schedule confirmations
- Coordinated decision-making
- Document sharing and verification

## Topic Progression
1. Schedule Management
   - Initial planning
   - Adjustments
   - Final arrangements

2. Financial Coordination
   - Expense sharing
   - Payment tracking
   - Reconciliation

3. Children's Activities
   - School coordination
   - Sports planning
   - Healthcare arrangements

## Reference Threading
- See [Cross References](cross_references.md) for topic relationships
- Review [Threads](threads/) for conversation details
- Check [Topics](topics/) for subject analysis
"""
        with open(self.notebooklm_dir / "timeline.md", 'w', encoding='utf-8') as f:
            f.write(timeline)

    def _generate_cross_references(self):
        """Generate cross-reference document"""
        cross_refs = """# Cross-Reference Analysis

## Topic Relationships
1. Schedule & Activities
   - Visitation coordination
   - Sports and school events
   - Healthcare appointments

2. Financial & Property
   - Shared expenses
   - Maintenance costs
   - Future planning

3. Communication Patterns
   - Regular updates
   - Decision processes
   - Information sharing

## Document References
- School calendars
- Financial records
- Healthcare documentation
- Property records

## Thread Connections
- Schedule discussions → Activity planning
- Financial matters → Property decisions
- School events → Schedule coordination

## Search Guidelines
1. Temporal References
   - Use dates and times
   - Reference weeks
   - Consider time ranges

2. Topic References
   - Main categories
   - Subtopics
   - Cross-topic relationships

3. Document Connections
   - Related files
   - Supporting documents
   - Reference materials
"""
        with open(self.notebooklm_dir / "cross_references.md", 'w', encoding='utf-8') as f:
            f.write(cross_refs)

    def _generate_thread_documents(self):
        """Generate sample thread documents"""
        threads = {
            "schedule": {
                "title": "Schedule Coordination",
                "dates": "Dec 1-7, 2024",
                "topic": "Activity Planning"
            },
            "finance": {
                "title": "Financial Planning",
                "dates": "Dec 2-5, 2024",
                "topic": "Expense Sharing"
            },
            "property": {
                "title": "Property Matters",
                "dates": "Dec 3-6, 2024",
                "topic": "Maintenance Planning"
            }
        }
        
        for thread_id, thread in threads.items():
            content = f"""# Thread: {thread['title']}

## Overview
- Date Range: {thread['dates']}
- Topic: {thread['topic']}
- Status: Completed

## Key Points
- Initial discussion
- Clarifications
- Decision making
- Final arrangements

## Related Threads
- See [Timeline](../timeline.md)
- Check [Cross References](../cross_references.md)
"""
            with open(self.notebooklm_dir / "threads" / f"thread_{thread_id}.md", 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_topic_documents(self):
        """Generate sample topic documents"""
        topics = {
            "scheduling": "Schedule Management",
            "finance": "Financial Planning",
            "property": "Property Matters",
            "activities": "Children's Activities"
        }
        
        for topic_id, title in topics.items():
            content = f"""# Topic: {title}

## Overview
- Primary Focus
- Key Discussions
- Decisions Made
- Future Planning

## Related Topics
- Cross References
- Supporting Documents
- Timeline Context

## Search Tips
- Use specific dates
- Reference participants
- Include key terms
"""
            with open(self.notebooklm_dir / "topics" / f"topic_{topic_id}.md", 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_participant_documents(self):
        """Generate sample participant documents"""
        participants = ["parent1", "parent2"]
        
        for participant in participants:
            content = f"""# Participant: {participant}

## Communication Style
- Response Patterns
- Topic Focus
- Decision Making

## Key Interactions
- Schedule Management
- Financial Planning
- Activity Coordination

## Related Documents
- Timeline References
- Topic Connections
- Thread Participation
"""
            with open(self.notebooklm_dir / "participants" / f"{participant}.md", 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_index(self):
        """Generate index document"""
        index = """# Communication Analysis Index

## Main Documents
1. [Overview](00_Overview.md)
2. [Timeline](timeline.md)
3. [Cross References](cross_references.md)

## Analysis Sections
- [Threads](threads/)
- [Topics](topics/)
- [Participants](participants/)

## Search Guidelines
- Use dates for timeline searches
- Reference topics for subject analysis
- Include participant names for filtering

## Navigation Tips
- Start with Overview
- Follow cross-references
- Explore related documents
"""
        with open(self.notebooklm_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(index)

def main():
    generator = TestNotebookLMGenerator()
    generator.generate_test_documents()
    print(f"Generated NotebookLM documents in: {generator.notebooklm_dir}")

if __name__ == "__main__":
    main()