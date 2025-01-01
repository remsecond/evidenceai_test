from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict
import re

class ThreadAnalyzer:
    """Analyzes threaded messages to extract patterns and insights"""
    
    def __init__(self, threaded_data: Dict):
        self.threads = threaded_data['threads']
        self.metadata = threaded_data['metadata']
        
    def analyze_threads(self) -> Dict:
        """
        Performs comprehensive analysis of threaded messages.
        Returns dictionary of analysis results.
        """
        response_patterns = self._analyze_response_patterns()
        topic_patterns = self._analyze_topic_patterns()
        participant_patterns = self._analyze_participant_patterns()
        
        return {
            'metadata': {
                'stage': 'analysis',
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'success',
            'response_patterns': response_patterns,
            'topic_patterns': topic_patterns,
            'participant_patterns': participant_patterns,
            'validation': {
                'is_valid': True,
                'checks_performed': ['response_analysis', 'topic_analysis', 'participant_analysis'],
                'warnings': []
            }
        }
    
    def _analyze_response_patterns(self) -> Dict:
        """Analyzes response times and patterns within threads"""
        response_times = []
        thread_durations = []
        message_intervals = defaultdict(list)
        
        for thread_id, messages in self.threads.items():
            # Sort messages by timestamp
            sorted_msgs = sorted(messages, key=lambda x: x['timestamp'] if x['timestamp'] else '0')
            
            # Calculate response times
            for i in range(1, len(sorted_msgs)):
                curr_msg = sorted_msgs[i]
                prev_msg = sorted_msgs[i-1]
                
                if curr_msg['timestamp'] and prev_msg['timestamp']:
                    curr_time = datetime.fromisoformat(curr_msg['timestamp'])
                    prev_time = datetime.fromisoformat(prev_msg['timestamp'])
                    response_time = (curr_time - prev_time).total_seconds() / 3600  # hours
                    response_times.append(response_time)
                    
                    # Track intervals by participant pair
                    participant_pair = tuple(sorted([curr_msg['from'], prev_msg['from']]))
                    message_intervals[participant_pair].append(response_time)
            
            # Calculate thread duration
            if len(sorted_msgs) > 1:
                start_time = datetime.fromisoformat(sorted_msgs[0]['timestamp'])
                end_time = datetime.fromisoformat(sorted_msgs[-1]['timestamp'])
                duration = (end_time - start_time).total_seconds() / 3600  # hours
                thread_durations.append(duration)
        
        # Calculate statistics
        stats = {
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'median_response_time': sorted(response_times)[len(response_times)//2] if response_times else 0,
            'average_thread_duration': sum(thread_durations) / len(thread_durations) if thread_durations else 0,
            'participant_response_times': {
                '_'.join(pair): {
                    'average': sum(times) / len(times) if times else 0,
                    'count': len(times)
                }
                for pair, times in message_intervals.items()
            }
        }
        
        return stats
    
    def _analyze_topic_patterns(self) -> Dict:
        """Analyzes topic patterns and transitions within threads"""
        topic_frequencies = defaultdict(int)
        topic_transitions = defaultdict(int)
        
        for thread_id, messages in self.threads.items():
            # Count topic frequencies
            subject = self.metadata[thread_id]['subject']
            if subject:
                topic_frequencies[subject.lower()] += 1
            
            # Analyze topic transitions between threads
            for msg in messages:
                content = msg.get('content', '').lower()
                # Look for topic indicators
                topic_indicators = [
                    'regarding',
                    'about',
                    'subject',
                    'matter',
                    'issue'
                ]
                for indicator in topic_indicators:
                    if indicator in content:
                        # Extract potential topic transition
                        pattern = f"{indicator}\\s+([\\w\\s]+)"
                        matches = re.findall(pattern, content)
                        for match in matches:
                            topic_transitions[match.strip()] += 1
        
        return {
            'topic_frequencies': dict(topic_frequencies),
            'topic_transitions': dict(topic_transitions)
        }
    
    def _analyze_participant_patterns(self) -> Dict:
        """Analyzes participant interaction patterns"""
        participant_interactions = defaultdict(lambda: defaultdict(int))
        participant_initiatives = defaultdict(int)  # Who starts threads
        participant_responses = defaultdict(int)    # Who responds
        
        for thread_id, messages in self.threads.items():
            # Track thread initiator
            if messages:
                initiator = messages[0]['from']
                participant_initiatives[initiator] += 1
            
            # Track interactions
            for i in range(1, len(messages)):
                curr_msg = messages[i]
                prev_msg = messages[i-1]
                
                # Count responses
                participant_responses[curr_msg['from']] += 1
                
                # Track who responds to whom
                participant_interactions[prev_msg['from']][curr_msg['from']] += 1
        
        return {
            'interactions': {
                from_participant: dict(to_participants)
                for from_participant, to_participants in participant_interactions.items()
            },
            'initiatives': dict(participant_initiatives),
            'responses': dict(participant_responses)
        }