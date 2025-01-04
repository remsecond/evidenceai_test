"""
OFW Message Analysis Processor
----------------------------
Processes OFW message data and generates comprehensive analysis reports.

This module handles:
1. Timeline Analysis
2. Communication Analysis
3. Participant Analysis  
4. Statistical Summary
5. Final Report Generation
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional
import statistics
from collections import defaultdict

class OFWProcessor:
    """Main processor for OFW message analysis."""
    
    def __init__(self, base_dir: str = None):
        """Initialize processor with directory configuration."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        
        # Set up directory structure
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.notebooklm_dir = self.base_dir / "ab_tools_NotebookLM"
        self.chatgpt_dir = self.base_dir / "ab_tools_ChatGPT"
        
        # Ensure directories exist
        for dir_path in [self.input_dir, self.output_dir, self.notebooklm_dir, self.chatgpt_dir]:
            dir_path.mkdir(exist_ok=True)
            
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize analysis components
        self.messages = []
        self.timeline = {}
        self.patterns = {}
        self.participants = {}
        self.stats = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging with both file and console output."""
        logger = logging.getLogger('OFWProcessor')
        logger.setLevel(logging.DEBUG)
        
        # Console handler - INFO level
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console)
        
        # File handler - DEBUG level
        log_file = self.output_dir / 'processing.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        
        return logger
        
    def process_messages(self, input_file: str = "OFW_Messages_Report_Dec.pdf") -> bool:
        """Process OFW messages and generate all reports."""
        try:
            self.logger.info(f"Starting analysis of {input_file}")
            
            # Load messages
            if not self._load_messages():
                return False
                
            # Generate all analyses
            self.logger.info("Generating analyses...")
            
            self.timeline = self._analyze_timeline()
            self.patterns = self._analyze_patterns()
            self.participants = self._analyze_participants()
            self.stats = self._analyze_statistics()
            
            # Generate all reports
            self.logger.info("Generating reports...")
            
            success = all([
                self._generate_timeline_report(),
                self._generate_patterns_report(),
                self._generate_participant_report(),
                self._generate_statistics_report(),
                self._generate_final_report(),
                self._generate_notebooklm_format(),
                self._generate_llm_format()
            ])
            
            if success:
                self.logger.info("All reports generated successfully!")
                return True
            else:
                self.logger.error("Some reports failed to generate")
                return False
                
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            return False
            
    def _load_messages(self) -> bool:
        """Load messages from processed JSON."""
        try:
            messages_file = self.output_dir / "OFW_Messages_Report_Dec_messages.json"
            
            if not messages_file.exists():
                self.logger.error(f"Messages file not found: {messages_file}")
                return False
                
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.messages = data['messages']
            self.logger.info(f"Loaded {len(self.messages)} messages")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load messages: {str(e)}")
            return False
            
    def _analyze_timeline(self) -> Dict:
        """Generate timeline analysis with event sequences."""
        self.logger.info("Analyzing timeline...")
        
        timeline = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'message_count': len(self.messages),
                'date_range': {
                    'start': self.messages[0]['sent_time'],
                    'end': self.messages[-1]['sent_time']
                }
            },
            'events': [],
            'threads': {},
            'topics': {},
            'patterns': []
        }
        
        # Group messages by day
        days = {}
        for msg in self.messages:
            sent_time = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
            date_key = sent_time.strftime('%Y-%m-%d')
            
            if date_key not in days:
                days[date_key] = []
            days[date_key].append(msg)
        
        # Analyze each day
        for date, day_messages in sorted(days.items()):
            event = {
                'date': date,
                'message_count': len(day_messages),
                'participants': self._get_day_participants(day_messages),
                'topics': self._get_day_topics(day_messages),
                'threads': self._analyze_day_threads(day_messages),
                'response_times': self._analyze_day_responses(day_messages)
            }
            timeline['events'].append(event)
            
        # Identify patterns
        timeline['patterns'] = self._identify_timeline_patterns(timeline['events'])
        
        return timeline
        
    def _analyze_patterns(self) -> Dict:
        """Analyze communication patterns and behaviors."""
        self.logger.info("Analyzing communication patterns...")
        
        patterns = {
            'by_participant': {},
            'by_topic': {},
            'by_time': defaultdict(int),
            'threads': [],
            'interactions': []
        }
        
        # Process each message
        for msg in sorted(self.messages, key=lambda x: datetime.strptime(x['sent_time'], '%m/%d/%Y at %I:%M %p')):
            # Update participant stats
            self._update_participant_stats(patterns, msg)
            
            # Update topic stats
            self._update_topic_stats(patterns, msg)
            
            # Update time-based stats
            self._update_time_stats(patterns, msg)
            
            # Update thread tracking
            self._update_thread_stats(patterns, msg)
            
        # Analyze interaction patterns
        patterns['interactions'] = self._analyze_interactions()
        
        return patterns
        
    def _analyze_participants(self) -> Dict:
        """Generate detailed participant analysis."""
        self.logger.info("Analyzing participants...")
        
        participants = {
            'summary': {},
            'interactions': {},
            'relationships': {}
        }
        
        # Process each message
        for msg in self.messages:
            sender = msg['from']
            receiver = msg['to']
            
            # Initialize participant records
            for person in [sender, receiver]:
                if person not in participants['summary']:
                    participants['summary'][person] = self._init_participant_record()
            
            # Update participant stats
            self._update_participant_metrics(participants, msg)
            
            # Track participant relationships
            self._update_relationship_metrics(participants, msg)
        
        # Calculate derived metrics
        participants['metrics'] = self._calculate_participant_metrics(participants)
        
        return participants
        
    def _analyze_statistics(self) -> Dict:
        """Generate statistical analysis and metrics."""
        self.logger.info("Generating statistical analysis...")
        
        stats = {
            'message_metrics': self._calculate_message_metrics(),
            'response_metrics': self._calculate_response_metrics(),
            'topic_metrics': self._calculate_topic_metrics(),
            'interaction_metrics': self._calculate_interaction_metrics()
        }
        
        return stats
        
    def _generate_timeline_report(self) -> bool:
        """Generate timeline analysis report."""
        try:
            output_file = self.output_dir / 'timeline_analysis.txt'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write report
                self._write_timeline_report(f, self.timeline)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate timeline report: {str(e)}")
            return False
            
    def _generate_patterns_report(self) -> bool:
        """Generate communication patterns report."""
        try:
            output_file = self.output_dir / 'communication_patterns.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate patterns report: {str(e)}")
            return False
            
    def _generate_participant_report(self) -> bool:
        """Generate participant analysis report."""
        try:
            output_file = self.output_dir / 'participant_summary.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.participants, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate participant report: {str(e)}")
            return False
            
    def _generate_statistics_report(self) -> bool:
        """Generate statistical summary report."""
        try:
            output_file = self.output_dir / 'statistical_summary.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate statistics report: {str(e)}")
            return False
            
    def _generate_final_report(self) -> bool:
        """Generate comprehensive final report."""
        try:
            output_file = self.output_dir / 'final_report.txt'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                self._write_final_report(f)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate final report: {str(e)}")
            return False
            
    def _generate_notebooklm_format(self) -> bool:
        """Generate NotebookLM-formatted analysis."""
        try:
            # Generate main analysis document
            main_file = self.notebooklm_dir / 'OFW_Messages_Analysis.txt'
            with open(main_file, 'w', encoding='utf-8') as f:
                self._write_notebooklm_analysis(f)
            
            # Generate chronological message log
            log_file = self.notebooklm_dir / 'OFW_Messages_Log.txt'
            with open(log_file, 'w', encoding='utf-8') as f:
                self._write_notebooklm_log(f)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate NotebookLM format: {str(e)}")
            return False
            
    def _generate_llm_format(self) -> bool:
        """Generate LLM-optimized analysis format."""
        try:
            # Generate main analysis document
            analysis_file = self.chatgpt_dir / 'OFW_Analysis.txt'
            with open(analysis_file, 'w', encoding='utf-8') as f:
                self._write_llm_analysis(f)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate LLM format: {str(e)}")
            return False