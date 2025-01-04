from pathlib import Path
import logging
from datetime import datetime
import json
from collections import defaultdict
import time

from ..parsers.pdf_parser import OFWParser

class ProcessingState:
    """Track pipeline progress and issues"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        self.processing_time = {}
        
    def start_stage(self, stage):
        self.processing_time[stage] = {'start': time.time()}
        
    def end_stage(self, stage):
        self.processing_time[stage]['end'] = time.time()
        self.processing_time[stage]['duration'] = (
            self.processing_time[stage]['end'] - 
            self.processing_time[stage]['start']
        )
        
    def add_error(self, error):
        self.errors.append(error)
        
    def add_warning(self, warning):
        self.warnings.append(warning)
        
    def increment_stat(self, stat_name):
        self.stats[stat_name] += 1

class PreprocessingPipeline:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        """Configure logging"""
        log_dir = self.base_dir / 'output'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / 'pipeline.log')
            ]
        )
        return logging.getLogger(__name__)
        
    def process(self, input_files, output_types=None):
        """Main processing pipeline"""
        state = ProcessingState()
        outputs = {}
        
        try:
            # Step 1: Parse PDFs
            state.start_stage('parsing')
            self.logger.info("Starting PDF parsing...")
            
            parsed_data = {}
            for input_file in input_files:
                self.logger.info(f"Processing file: {input_file}")
                parser = OFWParser(input_file, self.base_dir / 'output')
                result = parser.parse_pdf()
                if result['status'] == 'success':
                    parsed_data[input_file.name] = result
                    state.increment_stat('parsed_files')
                    self.logger.info(f"Successfully parsed {input_file.name}")
                else:
                    error_msg = f"Failed to parse {input_file.name}: {result.get('error')}"
                    state.add_error(error_msg)
                    self.logger.error(error_msg)
            
            state.end_stage('parsing')
            
            if not parsed_data:
                raise Exception("No files were successfully parsed")
            
            # Step 2: Structure data
            state.start_stage('structuring')
            self.logger.info("Structuring data...")
            structured_data = self.structure_data(parsed_data, state)
            state.end_stage('structuring')
            
            # Step 3: Generate outputs
            state.start_stage('output_generation')
            self.logger.info("Generating outputs...")
            
            if not output_types or 'json' in output_types:
                outputs['json'] = self.generate_json(structured_data)
                state.increment_stat('json_files')
                self.logger.info("Generated JSON outputs")
            
            if not output_types or 'notebooklm' in output_types:
                outputs['notebooklm'] = self.generate_notebook(structured_data)
                state.increment_stat('notebook_files')
                self.logger.info("Generated NotebookLM format")
            
            if not output_types or 'summary' in output_types:
                outputs['summary'] = self.generate_summary(structured_data)
                state.increment_stat('summary_files')
                self.logger.info("Generated summary")
                
            state.end_stage('output_generation')
            
            self.logger.info("Pipeline completed successfully")
            return outputs, state
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}")
            state.add_error(str(e))
            return None, state
            
    def structure_data(self, parsed_data, state):
        """Structure parsed data into a unified format"""
        self.logger.info("Beginning data structuring...")
        
        structured = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'source_files': list(parsed_data.keys()),
                'total_messages': 0,
                'participants': defaultdict(set)
            },
            'messages': [],
            'threads': defaultdict(list)
        }
        
        for source, data in parsed_data.items():
            self.logger.info(f"Processing data from {source}")
            
            # Update metadata
            if 'metadata' in data:
                for key, value in data['metadata'].items():
                    if key == 'participants':
                        # Merge participant lists
                        for role, people in value.items():
                            structured['metadata']['participants'][role].update(people)
                    else:
                        structured['metadata'][key] = value
            
            # Process messages
            message_id = len(structured['messages'])  # Start from current count
            for msg in data.get('messages', []):
                message_id += 1
                msg_id = f"msg_{message_id:04d}"
                
                # Add message with ID
                msg['id'] = msg_id
                msg['source_file'] = source
                structured['messages'].append(msg)
                structured['metadata']['total_messages'] += 1
                
                # Track participants
                if msg.get('from'):
                    structured['metadata']['participants']['from'].add(msg['from'])
                if msg.get('to'):
                    to_name = msg['to'].split('(')[0].strip()  # Remove viewing info
                    structured['metadata']['participants']['to'].add(to_name)
                    
                # Group into threads
                thread_id = msg.get('subject', '').replace('Re: ', '').strip()
                if thread_id:
                    structured['threads'][thread_id].append(msg_id)
        
        # Convert sets to lists for JSON serialization
        structured['metadata']['participants'] = {
            k: sorted(v) for k, v in structured['metadata']['participants'].items()
        }
        
        # Convert thread defaultdict to regular dict
        structured['threads'] = dict(structured['threads'])
        
        self.logger.info(f"Structured {len(structured['messages'])} messages into {len(structured['threads'])} threads")
        return structured
    
    def generate_json(self, data):
        """Generate JSON output files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Messages JSON
        messages_file = self.base_dir / 'output' / 'json' / 'messages' / f'messages_{timestamp}.json'
        messages_file.parent.mkdir(parents=True, exist_ok=True)
        
        messages_output = {
            'metadata': data['metadata'],
            'messages': data['messages'],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages_output, f, indent=2)
            
        # Threads JSON
        threads_file = self.base_dir / 'output' / 'json' / 'threads' / f'threads_{timestamp}.json'
        threads_file.parent.mkdir(parents=True, exist_ok=True)
        
        thread_output = {
            'metadata': data['metadata'],
            'threads': data['threads'],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(threads_file, 'w', encoding='utf-8') as f:
            json.dump(thread_output, f, indent=2)
            
        return {
            'messages': messages_file,
            'threads': threads_file
        }
    
    def generate_notebook(self, data):
        """Generate NotebookLM formatted output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.base_dir / 'output' / 'text' / 'notebooks' / f'conversation_{timestamp}.txt'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Conversation Thread: OFW Communications\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
            
            # Write participants
            all_participants = set()
            for role in ['from', 'to']:
                if role in data['metadata']['participants']:
                    all_participants.update(data['metadata']['participants'][role])
            f.write(f"Participants: {', '.join(sorted(all_participants))}\n\n")
            
            # Write statistics
            f.write("## Summary Statistics\n")
            f.write(f"Total Messages: {data['metadata']['total_messages']}\n")
            f.write(f"Total Threads: {len(data['threads'])}\n\n")
            
            # Write messages by thread
            for thread_id, message_ids in data['threads'].items():
                f.write(f"## Thread: {thread_id}\n\n")
                
                # Get messages in this thread
                thread_messages = [
                    msg for msg in data['messages'] 
                    if msg['id'] in message_ids
                ]
                
                # Sort by timestamp
                thread_messages.sort(key=lambda x: x.get('timestamp', ''))
                
                # Write messages
                for msg in thread_messages:
                    time_str = msg.get('sent_time', 'Unknown Time')
                    f.write(f"[{msg['from']}] {time_str} - {msg['content']}\n")
                    if msg.get('first_viewed'):
                        f.write(f"(Viewed: {msg['first_viewed']})\n")
                    f.write("\n")
                
                f.write("-" * 80 + "\n\n")
                
        return output_file
    
    def generate_summary(self, data):
        """Generate summary output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.base_dir / 'output' / 'text' / 'summaries' / f'summary_{timestamp}.txt'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Communication Summary\n")
            f.write("===================\n\n")
            
            # Key statistics
            f.write("Key Points:\n")
            f.write(f"- Total Messages: {data['metadata']['total_messages']}\n")
            f.write(f"- Total Threads: {len(data['threads'])}\n")
            f.write(f"- Active Participants: {len(data['metadata']['participants'].get('from', []))}\n\n")
            
            # Participant activity
            f.write("Statistics:\n")
            f.write("- Participant Activity:\n")
            for participant in sorted(data['metadata']['participants'].get('from', [])):
                count = sum(1 for msg in data['messages'] if msg['from'] == participant)
                f.write(f"  * {participant}: {count} messages\n")
            
            # Thread activity
            f.write("\n- Thread Activity:\n")
            for thread_id, message_ids in sorted(data['threads'].items()):
                f.write(f"  * {thread_id}: {len(message_ids)} messages\n")
                
        return output_file

def main():
    """Run pipeline on test data"""
    base_dir = Path("C:/Users/robmo/OneDrive/Documents/evidenceai_test")
    pipeline = PreprocessingPipeline(base_dir)
    
    # Process input files
    input_files = [base_dir / "input" / "OFW_Messages_Report_Dec.pdf"]
    outputs, state = pipeline.process(input_files)
    
    if outputs:
        print("\nProcessing completed successfully!")
        print("\nOutput files:")
        for output_type, files in outputs.items():
            print(f"\n{output_type.upper()}:")
            if isinstance(files, dict):
                for name, path in files.items():
                    print(f"- {name}: {path}")
            else:
                print(f"- {files}")
    else:
        print("\nProcessing failed!")
        print("\nErrors:")
        for error in state.errors:
            print(f"- {error}")
            
        print("\nWarnings:")
        for warning in state.warnings:
            print(f"- {warning}")

if __name__ == "__main__":
    main()