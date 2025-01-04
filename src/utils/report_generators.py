"""
Report Generation Methods
------------------------
Handles generation of all analysis reports for OFW messages.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional
import statistics
from collections import defaultdict

class ReportGenerator:
    """Main report generation class."""
    
    def __init__(self, base_dir: str = None):
        """Initialize generator with directory structure."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.notebooklm_dir = self.base_dir / "ab_tools_NotebookLM"
        self.chatgpt_dir = self.base_dir / "ab_tools_ChatGPT"
        
        # Ensure directories exist
        for dir_path in [self.input_dir, self.output_dir, self.notebooklm_dir, self.chatgpt_dir]:
            dir_path.mkdir(exist_ok=True)
            
    def generate_reports(self, messages: List[Dict]) -> bool:
        """Generate all required reports."""
        try:
            # Generate each report type
            timeline_ok = self.generate_timeline(messages)
            patterns_ok = self.generate_patterns(messages)
            participants_ok = self.generate_participants(messages)
            stats_ok = self.generate_statistics(messages)
            final_ok = self.generate_final_report(messages)
            llm_ok = self.generate_llm_formats(messages)
            
            return all([timeline_ok, patterns_ok, participants_ok, stats_ok, final_ok, llm_ok])
        
        except Exception as e:
            print(f"Error generating reports: {str(e)}")
            return False
            
    def generate_timeline(self, messages: List[Dict]) -> bool:
        """Generate timeline analysis report."""
        output_file = self.output_dir / "timeline_analysis.txt"
        
        try:
            # Group messages by day
            days = defaultdict(list)
            for msg in messages:
                sent_time = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
                days[sent_time.strftime('%Y-%m-%d')].append(msg)
            
            # Generate report
            with open(output_file, 'w', encoding='utf-8') as f:
                # Header
                f.write("OFW COMMUNICATIONS TIMELINE ANALYSIS\n")
                f.write("===================================\n\n")
                
                # Overview
                f.write("OVERVIEW\n")
                f.write("--------\n")
                f.write(f"Total Messages: {len(messages)}\n")
                f.write(f"Date Range: {messages[0]['sent_time']} to {messages[-1]['sent_time']}\n")
                f.write(f"Active Days: {len(days)}\n")
                f.write("\nKey Topics:\n")
                
                # Identify key topics
                topics = defaultdict(int)
                for msg in messages:
                    if msg.get('subject'):
                        topics[msg['subject'].replace('Re: ', '')] += 1
                
                for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]:
                    f.write(f"- {topic}: {count} messages\n")
                
                # Daily Timeline
                f.write("\nDAILY TIMELINE\n")
                f.write("--------------\n\n")
                
                for date in sorted(days.keys()):
                    day_messages = days[date]
                    participants = set()
                    day_topics = defaultdict(int)
                    
                    for msg in day_messages:
                        participants.add(msg['from'])
                        participants.add(msg['to'])
                        if msg.get('subject'):
                            day_topics[msg['subject'].replace('Re: ', '')] += 1
                    
                    f.write(f"Date: {date}\n")
                    f.write(f"Messages: {len(day_messages)}\n")
                    f.write(f"Participants: {', '.join(sorted(participants))}\n")
                    
                    if day_topics:
                        f.write("\nTopics Discussed:\n")
                        for topic, count in sorted(day_topics.items(), key=lambda x: x[1], reverse=True):
                            f.write(f"- {topic}: {count} messages\n")
                    
                    f.write("\nMessage Timeline:\n")
                    for msg in sorted(day_messages, key=lambda x: x['sent_time']):
                        f.write(f"- {msg['sent_time']} | From: {msg['from']} to {msg['to']}\n")
                        if msg.get('subject'):
                            f.write(f"  Subject: {msg['subject']}\n")
                            
                    f.write("\n" + "-"*50 + "\n\n")
            
            return True
            
        except Exception as e:
            print(f"Error generating timeline report: {str(e)}")
            return False
            
    def generate_patterns(self, messages: List[Dict]) -> bool:
        """Generate communication patterns report."""
        output_file = self.output_dir / "communication_patterns.json"
        
        try:
            patterns = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_messages': len(messages)
                },
                'participant_patterns': self._analyze_participant_patterns(messages),
                'topic_patterns': self._analyze_topic_patterns(messages),
                'time_patterns': self._analyze_time_patterns(messages),
                'response_patterns': self._analyze_response_patterns(messages)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error generating patterns report: {str(e)}")
            return False
            
    def _analyze_participant_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze participant communication patterns."""
        patterns = {}
        
        for msg in messages:
            sender = msg['from']
            receiver = msg['to']
            
            for participant in [sender, receiver]:
                if participant not in patterns:
                    patterns[participant] = {
                        'sent': 0,
                        'received': 0,
                        'topics_initiated': set(),
                        'response_times': [],
                        'common_contacts': defaultdict(int),
                        'active_hours': defaultdict(int)
                    }
            
            # Update counts
            patterns[sender]['sent'] += 1
            patterns[receiver]['received'] += 1
            patterns[sender]['common_contacts'][receiver] += 1
            
            # Track topics
            if msg.get('subject') and not msg['subject'].startswith('Re:'):
                patterns[sender]['topics_initiated'].add(msg['subject'])
            
            # Track response times
            if msg.get('first_viewed') and msg['first_viewed'] != 'Never':
                sent = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
                viewed = datetime.strptime(msg['first_viewed'], '%m/%d/%Y at %I:%M %p')
                response_time = (viewed - sent).total_seconds() / 60
                patterns[receiver]['response_times'].append(response_time)
            
            # Track activity hours
            sent_time = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
            patterns[sender]['active_hours'][sent_time.hour] += 1
        
        # Convert sets and calculate averages
        for p in patterns.values():
            p['topics_initiated'] = list(p['topics_initiated'])
            if p['response_times']:
                p['avg_response_time'] = sum(p['response_times']) / len(p['response_times'])
                p['min_response_time'] = min(p['response_times'])
                p['max_response_time'] = max(p['response_times'])
            
            # Convert defaultdicts to regular dicts
            p['common_contacts'] = dict(p['common_contacts'])
            p['active_hours'] = dict(p['active_hours'])
        
        return patterns
        
    def _analyze_topic_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze topic-based communication patterns."""
        topics = defaultdict(lambda: {
            'messages': 0,
            'participants': set(),
            'timeline': [],
            'response_times': []
        })
        
        for msg in messages:
            if msg.get('subject'):
                topic = msg['subject'].replace('Re: ', '')
                topics[topic]['messages'] += 1
                topics[topic]['participants'].add(msg['from'])
                topics[topic]['participants'].add(msg['to'])
                topics[topic]['timeline'].append({
                    'time': msg['sent_time'],
                    'from': msg['from'],
                    'to': msg['to']
                })
                
                if msg.get('first_viewed') and msg['first_viewed'] != 'Never':
                    sent = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
                    viewed = datetime.strptime(msg['first_viewed'], '%m/%d/%Y at %I:%M %p')
                    response_time = (viewed - sent).total_seconds() / 60
                    topics[topic]['response_times'].append(response_time)
        
        # Convert sets and calculate averages
        patterns = {}
        for topic, data in topics.items():
            patterns[topic] = {
                'message_count': data['messages'],
                'participants': list(data['participants']),
                'timeline': data['timeline'],
                'avg_response_time': (
                    sum(data['response_times']) / len(data['response_times'])
                    if data['response_times'] else None
                )
            }
        
        return patterns
        
    def _analyze_time_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze temporal communication patterns."""
        patterns = {
            'hourly': defaultdict(int),
            'daily': defaultdict(int),
            'response_times': defaultdict(list)
        }
        
        for msg in messages:
            sent_time = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
            patterns['hourly'][sent_time.hour] += 1
            patterns['daily'][sent_time.strftime('%A')] += 1
            
            if msg.get('first_viewed') and msg['first_viewed'] != 'Never':
                viewed = datetime.strptime(msg['first_viewed'], '%m/%d/%Y at %I:%M %p')
                response_time = (viewed - sent_time).total_seconds() / 60
                patterns['response_times'][sent_time.hour].append(response_time)
        
        # Calculate hourly averages
        hourly_stats = {}
        for hour, count in patterns['hourly'].items():
            hourly_stats[hour] = {
                'message_count': count,
                'avg_response_time': (
                    sum(patterns['response_times'][hour]) / len(patterns['response_times'][hour])
                    if patterns['response_times'][hour] else None
                )
            }
        
        return {
            'hourly_patterns': dict(hourly_stats),
            'daily_patterns': dict(patterns['daily'])
        }
        
    def _analyze_response_patterns(self, messages: List[Dict]) -> Dict:
        """Analyze response time patterns."""
        patterns = {
            'by_participant': defaultdict(list),
            'by_topic': defaultdict(list),
            'by_time': defaultdict(list),
            'overall': []
        }
        
        for msg in messages:
            if msg.get('first_viewed') and msg['first_viewed'] != 'Never':
                sent = datetime.strptime(msg['sent_time'], '%m/%d/%Y at %I:%M %p')
                viewed = datetime.strptime(msg['first_viewed'], '%m/%d/%Y at %I:%M %p')
                response_time = (viewed - sent).total_seconds() / 60
                
                patterns['overall'].append(response_time)
                patterns['by_participant'][msg['to']].append(response_time)
                
                if msg.get('subject'):
                    topic = msg['subject'].replace('Re: ', '')
                    patterns['by_topic'][topic].append(response_time)
                
                hour = sent.hour
                patterns['by_time'][hour].append(response_time)
        
        # Calculate statistics
        stats = {
            'overall': self._calculate_response_stats(patterns['overall']),
            'by_participant': {
                p: self._calculate_response_stats(times)
                for p, times in patterns['by_participant'].items()
            },
            'by_topic': {
                t: self._calculate_response_stats(times)
                for t, times in patterns['by_topic'].items()
            },
            'by_time': {
                h: self._calculate_response_stats(times)
                for h, times in patterns['by_time'].items()
            }
        }
        
        return stats
        
    def _calculate_response_stats(self, times: List[float]) -> Dict:
        """Calculate response time statistics."""
        if not times:
            return None
            
        return {
            'average': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
        
    def generate_participants(self, messages: List[Dict]) -> bool:
        """Generate participant analysis report."""
        output_file = self.output_dir / "participant_summary.json"
        
        try:
            summary = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_messages': len(messages)
                },
                'participants': self._analyze_participants(messages),
                'relationships': self._analyze_relationships(messages),
                'engagement_metrics': self._calculate_engagement(messages)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error generating participant summary: {str(e)}")
            return False