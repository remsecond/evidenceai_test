"""Generate comprehensive analysis reports from processed OFW data."""

import json
import os
from datetime import datetime
from pathlib import Path
import re

class ReportGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.input_json = self.output_dir / "OFW_Messages_Report_Dec_messages.json"
        
    def generate_all_reports(self):
        """Generate all analysis reports."""
        print("\nGenerating analysis reports...")
        
        try:
            # Load processed data
            with open(self.input_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            messages = data['messages']
            
            # Generate each report
            self._generate_timeline(messages)
            self._generate_communication_patterns(messages)
            self._generate_participant_summary(messages)
            self._generate_statistical_summary(messages)
            self._generate_final_report(messages, data)
            
            print("Report generation complete!")
            return True
            
        except Exception as e:
            print(f"Error generating reports: {str(e)}")
            return False
            
    def _generate_timeline(self, messages):
        """Generate timeline analysis."""
        timeline_file = self.output_dir / "timeline_analysis.txt"
        
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write("OFW Communications Timeline Analysis\n")
            f.write("===================================\n\n")
            
            # Sort messages by date
            for msg in sorted(messages, key=lambda x: x['sent_time']):
                f.write(f"Date: {msg['sent_time']}\n")
                f.write(f"From: {msg['from']}\n")
                f.write(f"To: {msg['to']}\n")
                if msg.get('subject'):
                    f.write(f"Subject: {msg['subject']}\n")
                if msg.get('first_viewed'):
                    f.write(f"First Viewed: {msg['first_viewed']}\n")
                f.write("-" * 50 + "\n\n")
                
    def _generate_communication_patterns(self, messages):
        """Generate communication pattern analysis."""
        patterns_file = self.output_dir / "communication_patterns.json"
        
        # Analyze patterns
        patterns = {
            'by_participant': {},
            'response_times': [],
            'common_subjects': {},
            'time_of_day': {
                'morning': 0,
                'afternoon': 0,
                'evening': 0,
                'night': 0
            }
        }
        
        # Process messages
        for msg in messages:
            # Count messages by participant
            sender = msg['from']
            if sender not in patterns['by_participant']:
                patterns['by_participant'][sender] = {
                    'sent': 0,
                    'received': 0
                }
            patterns['by_participant'][sender]['sent'] += 1
            
            receiver = msg['to']
            if receiver not in patterns['by_participant']:
                patterns['by_participant'][receiver] = {
                    'sent': 0,
                    'received': 0
                }
            patterns['by_participant'][receiver]['received'] += 1
            
            # Count subjects
            if msg.get('subject'):
                subject = msg['subject']
                patterns['common_subjects'][subject] = patterns['common_subjects'].get(subject, 0) + 1
        
        # Save patterns
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
                
    def _generate_participant_summary(self, messages):
        """Generate participant interaction summary."""
        summary_file = self.output_dir / "participant_summary.json"
        
        participants = {}
        
        # Analyze each message
        for msg in messages:
            sender = msg['from']
            receiver = msg['to']
            
            # Initialize participant data
            for p in [sender, receiver]:
                if p not in participants:
                    participants[p] = {
                        'messages_sent': 0,
                        'messages_received': 0,
                        'response_times': [],
                        'common_recipients': {},
                        'subjects_initiated': set()
                    }
            
            # Update counts
            participants[sender]['messages_sent'] += 1
            participants[receiver]['messages_received'] += 1
            
            # Track subject initiation
            if msg.get('subject'):
                participants[sender]['subjects_initiated'].add(msg['subject'])
        
        # Convert sets to lists for JSON serialization
        for p in participants:
            participants[p]['subjects_initiated'] = list(participants[p]['subjects_initiated'])
        
        # Save summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(participants, f, indent=2)
                
    def _generate_statistical_summary(self, messages):
        """Generate statistical analysis summary."""
        stats_file = self.output_dir / "statistical_summary.json"
        
        stats = {
            'total_messages': len(messages),
            'date_range': {
                'start': messages[0]['sent_time'],
                'end': messages[-1]['sent_time']
            },
            'message_counts': {
                'by_sender': {},
                'by_month': {},
                'by_day': {}
            },
            'response_metrics': {
                'average_time': None,
                'shortest': None,
                'longest': None
            }
        }
        
        # Calculate statistics
        for msg in messages:
            # Count by sender
            sender = msg['from']
            stats['message_counts']['by_sender'][sender] = stats['message_counts']['by_sender'].get(sender, 0) + 1
        
        # Save statistics
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
                
    def _generate_final_report(self, messages, data):
        """Generate final comprehensive report."""
        report_file = self.output_dir / "final_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("OFW Communications Analysis Report\n")
            f.write("=================================\n\n")
            
            # Overview
            f.write("Overview\n")
            f.write("--------\n")
            f.write(f"Total Messages: {len(messages)}\n")
            f.write(f"Date Range: {messages[0]['sent_time']} to {messages[-1]['sent_time']}\n")
            f.write(f"Source File: {data['source_file']}\n\n")
            
            # Participant Summary
            participants = set()
            for msg in messages:
                participants.add(msg['from'])
                participants.add(msg['to'])
                
            f.write("Participants\n")
            f.write("-----------\n")
            for p in sorted(participants):
                sent_count = len([m for m in messages if m['from'] == p])
                received_count = len([m for m in messages if m['to'] == p])
                f.write(f"{p}:\n")
                f.write(f"  Messages Sent: {sent_count}\n")
                f.write(f"  Messages Received: {received_count}\n")
            f.write("\n")
            
            # Key Observations
            f.write("Key Observations\n")
            f.write("---------------\n")
            # Add observations based on patterns...
            f.write("\n")

def main():
    """Main execution function."""
    generator = ReportGenerator()
    if generator.generate_all_reports():
        print("\nAll reports generated successfully!")
    else:
        print("\nError generating reports!")

if __name__ == '__main__':
    main()