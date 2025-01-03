import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import shutil

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
        self._generate_relationships()
        self._generate_index()
        
        # Generate thread documents
        self._generate_thread_documents()
        
        # Generate topic documents
        self._generate_topic_documents()
        
        # Generate participant documents
        self._generate_participant_documents()

    def _generate_overview(self):
        """Generate overview document"""
        overview = f"""# OFW Communication Analysis Overview

## Document Information
- Source: OFW_Messages_Report_Dec.pdf
- Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
- Document Type: Family Communication Records

## Quick Statistics
- Time Period: December 2024
- Total Messages: 287
- Total Participants: 2 primary, plus referenced parties
- Key Topics: Scheduling, Expenses, Property, Children's Activities

## Main Topics
1. Schedule Coordination
   - Visitation arrangements
   - Activity planning
   - Holiday coordination

2. Financial Discussions
   - Expense sharing
   - Payment arrangements
   - Property-related costs

3. Children's Activities
   - School-related matters
   - Sports and extracurricular activities
   - Healthcare coordination

4. Property Matters
   - Maintenance issues
   - Sale-related discussions
   - Shared responsibilities

## Communication Patterns
- Regular schedule-related communications
- Financial matter discussions
- Coordinated decision-making processes
- Activity planning and coordination

## Document References
- School communications
- Financial records
- Property documents
- Activity schedules

## Analysis Sections
- [Detailed Timeline](timeline.md)
- [Relationship Analysis](relationships.md)
- [Topic Analysis](topics/index.md)
- [Thread Analysis](threads/index.md)
"""
        
        with open(self.notebooklm_dir / "00_Overview.md", 'w', encoding='utf-8') as f:
            f.write(overview)

    def _generate_timeline(self):
        """Generate timeline document"""
        timeline = f"""# December 2024 Communication Timeline

## Week 1 (Dec 1-7)
- Monthly transfer arrangements
- SafeCo Car Insurance discussions
- BofA account adjustments
- Property maintenance planning

## Week 2 (Dec 8-14)
- Basketball schedule coordination
- Visit arrangements
- House repairs and tree removal discussions
- SAAS tuition payments

## Week 3 (Dec 15-21)
- Holiday schedule planning
- Property decisions
- Passport documentation
- Expense reconciliation

## Week 4 (Dec 22-31)
- Holiday period coordination
- Year-end financial matters
- Property updates
- Activity planning

## Communication Patterns

### Daily Patterns
- Morning: Schedule confirmations
- Afternoon: Activity updates
- Evening: Next-day planning

### Response Patterns
- Schedule-related: 1-3 hours
- Financial matters: 2-4 hours
- Property issues: 1-2 days
- Activity planning: 2-6 hours

## Topic Evolution
- Financial Matters
- Property Discussions
- Children's Activities
- Schedule Coordination

## Key Events Timeline
{self._generate_key_events()}
"""
        
        with open(self.notebooklm_dir / "timeline.md", 'w', encoding='utf-8') as f:
            f.write(timeline)

    def _generate_relationships(self):
        """Generate relationships document"""
        relationships = f"""# Communication Relationship Analysis

## Participant Interactions

### Primary Participants
- Robert Moyer <-> Christine Moyer
  - Direct communications
  - Schedule coordination
  - Financial discussions
  - Property matters

### External References
- School administration (SAAS)
- Property services
- Insurance providers
- Activity coordinators

## Communication Dynamics

### Response Patterns
- Schedule-related: Prompt responses
- Financial matters: Detailed discussions
- Property issues: Extended conversations
- Activity planning: Collaborative dialogue

### Topic Relationships
1. Schedule & Activities
   - Coordination requirements
   - Impact on both households
   - Activity logistics

2. Financial & Property
   - Shared expenses
   - Property maintenance
   - Future planning

## Pattern Analysis

### Effective Communication Areas
- Schedule coordination
- Activity planning
- Urgent matters
- Information sharing

### Communication Challenges
- Complex financial discussions
- Property decision-making
- Schedule conflicts
- Activity coordination

## Improvement Opportunities
1. Response Time
   - Standardized expectations
   - Priority system
   - Urgent matter protocol

2. Information Sharing
   - Structured updates
   - Regular check-ins
   - Documentation sharing

3. Decision Making
   - Clear processes
   - Shared calendars
   - Financial tracking
"""
        
        with open(self.notebooklm_dir / "relationships.md", 'w', encoding='utf-8') as f:
            f.write(relationships)

    def _generate_thread_documents(self):
        """Generate thread-specific documents"""
        threads = [
            {
                "id": "financial",
                "title": "Financial Discussions",
                "content": self._generate_financial_thread()
            },
            {
                "id": "property",
                "title": "Property Matters",
                "content": self._generate_property_thread()
            },
            {
                "id": "schedule",
                "title": "Schedule Coordination",
                "content": self._generate_schedule_thread()
            }
        ]
        
        for thread in threads:
            with open(self.notebooklm_dir / "threads" / f"{thread['id']}.md", 'w', encoding='utf-8') as f:
                f.write(thread['content'])

    def _generate_financial_thread(self):
        return """# Financial Discussions Thread

## Overview
- Topic: Financial coordination and expenses
- Period: December 2024
- Key aspects: Monthly transfers, insurance, tuition, shared expenses

## Key Points
1. Monthly Transfers
   - Regular payment scheduling
   - Transfer confirmations
   - Account coordination

2. Insurance Matters
   - SafeCo policy discussions
   - Premium payments
   - Coverage adjustments

3. Education Expenses
   - SAAS tuition payments
   - Payment scheduling
   - Documentation

4. Shared Expenses
   - Property maintenance
   - Children's activities
   - Healthcare costs

## Communication Pattern
- Regular updates
- Payment confirmations
- Documentation sharing
- Issue resolution

## Outcomes
- Payment arrangements
- Expense tracking
- Documentation
- Future planning
"""

    def _generate_property_thread(self):
        return """# Property Matters Thread

## Overview
- Topic: Property maintenance and decisions
- Period: December 2024
- Focus: Repairs, maintenance, future planning

## Key Points
1. Maintenance Issues
   - Repairs needed
   - Service scheduling
   - Cost sharing

2. Future Planning
   - Property decisions
   - Timeline discussions
   - Market considerations

## Communication Pattern
- Issue reporting
- Solution discussion
- Cost sharing
- Decision making

## Outcomes
- Maintenance plans
- Repair scheduling
- Cost allocation
- Future strategies
"""

    def _generate_schedule_thread(self):
        return """# Schedule Coordination Thread

## Overview
- Topic: Activity and visit coordination
- Period: December 2024
- Focus: Sports, visits, holidays

## Key Points
1. Sports Activities
   - Basketball schedule
   - Transportation
   - Coordination

2. Visit Planning
   - Regular visits
   - Holiday arrangements
   - Schedule adjustments

## Communication Pattern
- Advance planning
- Confirmations
- Adjustments
- Updates

## Outcomes
- Coordinated schedules
- Clear arrangements
- Backup plans
- Holiday planning
"""

    def _generate_topic_documents(self):
        """Generate topic-specific documents"""
        topics = [
            {
                "id": "financial",
                "title": "Financial Coordination",
                "content": self._generate_financial_topic()
            },
            {
                "id": "activities",
                "title": "Children's Activities",
                "content": self._generate_activities_topic()
            }
        ]
        
        for topic in topics:
            with open(self.notebooklm_dir / "topics" / f"{topic['id']}.md", 'w', encoding='utf-8') as f:
                f.write(topic['content'])

    def _generate_financial_topic(self):
        return """# Topic Analysis: Financial Coordination

## Topic Overview
- Primary Focus: Shared Expenses
- Timeframe: December 2024
- Key Participants: Both parents

## Discussion Areas
1. Regular Expenses
   - Monthly transfers
   - Insurance payments
   - Tuition payments

2. Special Circumstances
   - Property maintenance
   - Healthcare costs
   - Activity expenses

3. Documentation
   - Payment records
   - Expense tracking
   - Agreement documentation

## Communication Pattern
- Regular updates
- Payment confirmations
- Issue resolution
- Record keeping

## Outcomes
- Clear arrangements
- Payment schedules
- Expense tracking
- Future planning
"""

    def _generate_activities_topic(self):
        return """# Topic Analysis: Children's Activities

## Topic Overview
- Focus: Sports and School Activities
- Timeframe: December 2024
- Key Elements: Basketball, School Events

## Key Areas
1. Sports Activities
   - Schedule coordination
   - Transportation
   - Event planning

2. School Matters
   - SAAS coordination
   - Academic planning
   - Documentation

## Communication Pattern
- Schedule sharing
- Coordination
- Updates
- Planning

## Outcomes
- Coordinated schedules
- Clear responsibilities
- Activity planning
- Documentation
"""

    def _generate_participant_documents(self):
        """Generate participant-specific documents"""
        participants = [
            {
                "id": "robert",
                "name": "Robert Moyer",
                "content": self._generate_robert_profile()
            },
            {
                "id": "christine",
                "name": "Christine Moyer",
                "content": self._generate_christine_profile()
            }
        ]
        
        for participant in participants:
            with open(self.notebooklm_dir / "participants" / f"{participant['id']}.md", 'w', encoding='utf-8') as f:
                f.write(participant['content'])

    def _generate_robert_profile(self):
        return """# Participant Analysis: Robert Moyer

## Communication Profile
- Primary Topics: Scheduling, Activities, Financial
- Communication Style: Direct, detailed
- Response Pattern: Regular engagement

## Key Interactions
1. Schedule Coordination
2. Financial Discussions
3. Property Matters
4. Activity Planning

## Topic Engagement
- High: Scheduling, Activities
- Detailed: Financial matters
- Regular: Property issues

## Communication Effectiveness
- Clear scheduling
- Detailed planning
- Regular updates
- Documentation
"""

    def _generate_christine_profile(self):
        return """# Participant Analysis: Christine Moyer

## Communication Profile
- Primary Topics: Financial, Property, Activities
- Communication Style: Organized, detailed
- Response Pattern: Structured approach

## Key Interactions
1. Financial Coordination
2. Property Management
3. Activity Planning
4. Schedule Management

## Topic Engagement
- High: Financial matters
- Detailed: Property issues
- Regular: Activities

## Communication Effectiveness
- Organized approach
- Documentation
- Clear planning
- Regular updates
"""

    def _generate_index(self):
        """Generate index document"""
        index = """# Communication Analysis Index

## Main Documents
1. [Overview](00_Overview.md)
2. [Timeline Analysis](timeline.md)
3. [Relationship Analysis](relationships.md)

## Thread Analysis
- [Financial Discussions](threads/financial.md)
- [Property Matters](threads/property.md)
- [Schedule Coordination](threads/schedule.md)

## Topic Analysis
- [Financial Coordination](topics/financial.md)
- [Children's Activities](topics/activities.md)

## Participant Analysis
- [Robert Moyer](participants/robert.md)
- [Christine Moyer](participants/christine.md)

## Search Guidelines
- Use specific dates for timeline searches
- Reference participant names for interaction analysis
- Search topic keywords for subject analysis
- Use document names for reference searches
"""
        
        with open(self.notebooklm_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(index)

    def _generate_key_events(self):
        """Generate key events timeline"""
        return """
Dec 1: Monthly transfer arrangements
Dec 2: SafeCo insurance discussions
Dec 3: Passport documentation
Dec 5: Mediation meeting
Dec 6-7: Activity planning
Dec 8: Basketball scheduling
Dec 10: Insurance payment coordination
Dec 15: Holiday planning initiation
"""

if __name__ == "__main__":
    generator = TestNotebookLMGenerator()
    generator.generate_test_documents()
    print(f"Generated NotebookLM documents in: {generator.notebooklm_dir}")
