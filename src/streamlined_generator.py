from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

class StreamlinedNarrativeGenerator:
    """Generates clean, non-redundant narrative documents for NotebookLM"""
    
    def __init__(self, messages: List[Dict]):
        self.messages = sorted(messages, key=lambda x: x['timestamp'])
        self.days = self._group_by_day()
        self.threads = self._identify_threads()
    
    def _group_by_day(self) -> Dict[str, List[Dict]]:
        """Group messages by day"""
        days = {}
        for msg in self.messages:
            day = msg['timestamp'][:10]
            if day not in days:
                days[day] = []
            days[day].append(msg)
        return days
    
    def _identify_threads(self) -> Dict[str, List[Dict]]:
        """Identify message threads"""
        threads = {}
        for msg in self.messages:
            thread_id = msg.get('in_reply_to', msg['id'])
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(msg)
        return threads

    def _format_message(self, msg: Dict, prev_msg: Optional[Dict] = None) -> str:
        """Format a single message with context"""
        time = datetime.fromisoformat(msg['timestamp']).strftime('%-I:%M %p')
        
        # Calculate response time if it's a reply
        response_time = ""
        if prev_msg and msg.get('in_reply_to') == prev_msg['id']:
            time_diff = (datetime.fromisoformat(msg['timestamp']) - 
                        datetime.fromisoformat(prev_msg['timestamp']))
            minutes = int(time_diff.total_seconds() / 60)
            if minutes < 60:
                response_time = f" ({minutes}m response)"
        
        # Format base message
        narrative = f"{time}{response_time}: {msg['from']} to {msg['to']}"
        
        # Add subject if relevant and not redundant
        if msg.get('subject') and (not prev_msg or 
                                 msg['subject'] != prev_msg.get('subject')):
            narrative += f" regarding {msg['subject']}"
        
        # Add content
        if msg.get('content'):
            narrative += f". {msg['content']}"
        
        return narrative

    def _get_day_context(self, date: str) -> str:
        """Get relevant context for a day"""
        curr_date = datetime.fromisoformat(date)
        prev_date = (curr_date - timedelta(days=1)).strftime('%Y-%m-%d')
        next_date = (curr_date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        context = []
        
        # Look for related discussions
        related_threads = set()
        if prev_date in self.days:
            for msg in self.days[prev_date]:
                if any(future.get('in_reply_to') == msg['id'] 
                      for future in self.days.get(date, [])):
                    thread = self._get_thread_summary(msg)
                    if thread:
                        related_threads.add(thread)
        
        if related_threads:
            context.append("Related context: " + ". ".join(related_threads))
        
        return "\n".join(context) if context else ""

    def _get_thread_summary(self, msg: Dict) -> Optional[str]:
        """Get concise thread summary if relevant"""
        if msg['id'] not in self.threads:
            return None
            
        thread = self.threads[msg['id']]
        if len(thread) < 2:
            return None
            
        # Look for key topics or decisions
        topics = set(m.get('subject', '') for m in thread if m.get('subject'))
        if topics:
            return f"Continues discussion about {', '.join(topics)}"
        
        return None

    def generate_narrative(self, output_dir: Path) -> None:
        """Generate streamlined narrative document"""
        narrative = []
        
        for date in sorted(self.days.keys()):
            messages = self.days[date]
            
            # Add day header
            day_date = datetime.fromisoformat(date)
            narrative.append(f"# {day_date.strftime('%B %d, %Y')}\n")
            
            # Add messages
            prev_msg = None
            for msg in sorted(messages, key=lambda x: x['timestamp']):
                narrative.append(self._format_message(msg, prev_msg))
                prev_msg = msg
            
            # Add day context if relevant
            context = self._get_day_context(date)
            if context:
                narrative.append(f"\n{context}")
            
            narrative.append("\n")  # Space between days
        
        # Write to file
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "communication_narrative.md", 'w', encoding='utf-8') as f:
            f.write("\n".join(narrative))

def process_ofw_file(input_file: Path, output_dir: Path) -> None:
    """Process OFW file and generate narrative"""
    try:
        # Read and parse OFW data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generate narrative
        generator = StreamlinedNarrativeGenerator(data['messages'])
        generator.generate_narrative(output_dir)
        
        print(f"Generated narrative in {output_dir / 'communication_narrative.md'}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    base_dir = Path("C:/Users/robmo/OneDrive/Documents/evidenceai_test")
    input_file = base_dir / "output" / "OFW_Messages_Report_Dec" / "enriched_data.json"
    output_dir = base_dir / "output" / "OFW_Messages_Report_Dec" / "notebooklm_docs"
    
    process_ofw_file(input_file, output_dir)

if __name__ == "__main__":
    main()