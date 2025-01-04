"""Generate structured timelines for NotebookLM and LLMs."""
from datetime import datetime
from typing import List, Dict
import json

class TimelineGenerator:
    """Generate properly structured timelines."""
    
    def generate_notebooklm_timeline(self, messages: List[Dict], source_file: str) -> str:
        """Generate NotebookLM-formatted timeline."""
        # Sort messages by timestamp
        messages = sorted(messages, key=lambda x: x['timestamp'])
        
        output = []
        output.append("COMMUNICATION TIMELINE ANALYSIS")
        output.append("============================")
        output.append(f"Source: {source_file}")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Total Messages: {len(messages)}")
        output.append("")
        
        # Track threads by subject
        threads = {}
        for msg in messages:
            subject = msg.get('subject', 'No Subject')
            if subject not in threads:
                threads[subject] = []
            threads[subject].append(msg)
        
        # Write timeline by thread
        output.append("TIMELINE BY THREAD")
        output.append("=================")
        for subject, thread_msgs in threads.items():
            output.append(f"\nThread: {subject}")
            output.append("-" * len(f"Thread: {subject}"))
            
            for msg in sorted(thread_msgs, key=lambda x: x['timestamp']):
                output.append(f"\nTimestamp: {msg['sent_time']}")
                output.append(f"From: {msg['from']}")
                output.append(f"To: {msg['to']}")
                if msg.get('first_viewed'):
                    output.append(f"First Viewed: {msg['first_viewed']}")
                output.append("\nContent:")
                output.append("-" * 40)
                output.append(msg['content'])
                output.append("=" * 40)
        
        # Add chronological view
        output.append("\n\nCHRONOLOGICAL TIMELINE")
        output.append("=====================")
        
        current_date = None
        for msg in messages:
            msg_date = msg['sent_time'].split(' at ')[0]
            
            # Add date header when date changes
            if msg_date != current_date:
                current_date = msg_date
                output.append(f"\n{current_date}")
                output.append("-" * len(current_date))
            
            output.append(f"\n[{msg['sent_time']}]")
            output.append(f"Thread: {msg.get('subject', 'No Subject')}")
            output.append(f"From: {msg['from']} → To: {msg['to']}")
            if msg.get('first_viewed'):
                output.append(f"Viewed: {msg['first_viewed']}")
            output.append("\nContent:")
            output.append(msg['content'])
            output.append("-" * 40)
        
        return "\n".join(output)
    
    def generate_llm_timeline(self, messages: List[Dict], source_file: str) -> str:
        """Generate LLM-optimized timeline format."""
        # Sort messages by timestamp
        messages = sorted(messages, key=lambda x: x['timestamp'])
        
        output = []
        output.append("STRUCTURED COMMUNICATION TIMELINE")
        output.append("===============================")
        output.append("FORMAT: Timeline organized by date and thread, with clear message structure and relationships.")
        output.append("")
        
        output.append("METADATA:")
        output.append(f"Source File: {source_file}")
        output.append(f"Total Messages: {len(messages)}")
        output.append(f"Date Range: {messages[0]['sent_time']} to {messages[-1]['sent_time']}")
        output.append("")
        
        # Group by thread
        threads = {}
        for msg in messages:
            subject = msg.get('subject', 'No Subject')
            if subject not in threads:
                threads[subject] = []
            threads[subject].append(msg)
        
        output.append("THREAD OVERVIEW:")
        for subject, thread_msgs in threads.items():
            output.append(f"\n[THREAD] {subject}")
            output.append(f"Messages: {len(thread_msgs)}")
            output.append(f"Timeline: {thread_msgs[0]['sent_time']} to {thread_msgs[-1]['sent_time']}")
            output.append(f"Participants: {', '.join(set(m['from'] for m in thread_msgs))}")
            output.append("-" * 60)
        
        output.append("\nDETAILED TIMELINE:")
        output.append("================")
        
        current_date = None
        for msg in messages:
            msg_date = msg['sent_time'].split(' at ')[0]
            
            # Add date header
            if msg_date != current_date:
                current_date = msg_date
                output.append(f"\n[DATE] {current_date}")
            
            # Message block
            output.append("\n[MESSAGE]")
            output.append(f"Timestamp: {msg['sent_time']}")
            output.append(f"Thread: {msg.get('subject', 'No Subject')}")
            output.append(f"From: {msg['from']}")
            output.append(f"To: {msg['to']}")
            if msg.get('first_viewed'):
                output.append(f"First Viewed: {msg['first_viewed']}")
            
            # Clean and format content
            content = msg['content']
            # Remove page numbers
            content = '\n'.join(line for line in content.split('\n') 
                              if not line.strip().startswith('Page') and 
                              not line.strip().endswith('of 358'))
            
            output.append("\nContent:")
            output.append("-" * 40)
            output.append(content.strip())
            output.append("=" * 60)
        
        return "\n".join(output)