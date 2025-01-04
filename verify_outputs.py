from pathlib import Path
import json
import logging
from datetime import datetime
import sys
import webbrowser
import os
import shutil

class OutputVerifier:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / 'output'
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def create_example_files(self):
        """Create example output files"""
        self.logger.info("Creating example files...")
        
        # Example message in JSON format
        message_example = {
            "metadata": {
                "source": "OFW_export.pdf",
                "date_range": "2024-12",
                "message_count": 2
            },
            "messages": [
                {
                    "id": "msg_001",
                    "timestamp": "2024-12-01T01:02:00",
                    "from": "Person A",
                    "to": "Person B",
                    "subject": "Weekend Schedule",
                    "content": "Can we discuss the weekend schedule?"
                },
                {
                    "id": "msg_002",
                    "timestamp": "2024-12-01T02:15:00",
                    "from": "Person B",
                    "to": "Person A",
                    "subject": "Re: Weekend Schedule",
                    "content": "Yes, what time works for you?"
                }
            ]
        }

        # Example thread in JSON format
        thread_example = {
            "thread_id": "thread_001",
            "topic": "Weekend Schedule",
            "messages": ["msg_001", "msg_002"],
            "participants": ["Person A", "Person B"],
            "start_time": "2024-12-01T01:02:00",
            "end_time": "2024-12-01T02:15:00"
        }

        # Example NotebookLM format
        notebook_example = """# Conversation Thread: Weekend Schedule
Date: 2024-12-01
Participants: Person A, Person B

[Person A] 01:02 AM - Can we discuss the weekend schedule?
[Person B] 02:15 AM - Yes, what time works for you?

Thread Statistics:
- Duration: 1 hour 13 minutes
- Messages: 2
- Response Time: 1 hour 13 minutes"""

        # Example summary
        summary_example = """Communication Summary
Date Range: December 1, 2024

Key Points:
- Topic focused on weekend scheduling
- Quick response turnaround (1h 13m)
- Direct and clear communication

Statistics:
- Total Messages: 2
- Average Response Time: 1h 13m
- Active Participants: 2"""

        # Create example files
        examples = {
            'json/messages/example_messages.json': message_example,
            'json/threads/example_thread.json': thread_example,
            'text/notebooks/example_thread.txt': notebook_example,
            'text/summaries/example_summary.txt': summary_example
        }

        for rel_path, content in examples.items():
            full_path = self.output_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if isinstance(content, dict):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2)
                else:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.logger.info(f"Created example file: {rel_path}")
            except Exception as e:
                self.logger.error(f"Error creating {rel_path}: {str(e)}")

    def verify_files(self):
        """Verify all output files"""
        self.logger.info("Verifying files...")
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'by_type': {}
        }

        # Check each output directory
        for dir_type in ['json/messages', 'json/threads', 'text/notebooks', 'text/summaries']:
            dir_path = self.output_dir / dir_type
            if not dir_path.exists():
                continue

            dir_results = {
                'files': [],
                'valid': 0,
                'invalid': 0
            }

            # Check each file in directory
            for file_path in dir_path.glob('*.*'):
                validation = self._validate_file(file_path)
                dir_results['files'].append({
                    'name': file_path.name,
                    'path': str(file_path.relative_to(self.output_dir)),
                    'valid': validation['valid'],
                    'issues': validation.get('issues', []),
                    'size': file_path.stat().st_size
                })

                if validation['valid']:
                    dir_results['valid'] += 1
                    results['valid'] += 1
                else:
                    dir_results['invalid'] += 1
                    results['invalid'] += 1
                
                results['total'] += 1

            results['by_type'][dir_type] = dir_results

        return results

    def _validate_file(self, file_path):
        """Validate a single file"""
        if file_path.suffix == '.json':
            return self._validate_json(file_path)
        else:
            return self._validate_text(file_path)

    def _validate_json(self, file_path):
        """Validate JSON file content"""
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)

            issues = []
            if 'messages' in file_path.parent.name:
                required = {'metadata', 'messages'}
                missing = required - set(data.keys())
                if missing:
                    issues.append(f"Missing required fields: {missing}")

                # Validate message content
                if 'messages' in data:
                    for i, msg in enumerate(data['messages']):
                        if not msg.get('content'):
                            issues.append(f"Empty content in message {i+1}")
                        if not msg.get('timestamp'):
                            issues.append(f"Missing timestamp in message {i+1}")

            elif 'threads' in file_path.parent.name:
                required = {'thread_id', 'messages', 'topic'}
                missing = required - set(data.keys())
                if missing:
                    issues.append(f"Missing required fields: {missing}")

            return {
                'valid': len(issues) == 0,
                'issues': issues
            }

        except json.JSONDecodeError:
            return {
                'valid': False,
                'issues': ['Invalid JSON format']
            }
        except Exception as e:
            return {
                'valid': False,
                'issues': [str(e)]
            }

    def _validate_text(self, file_path):
        """Validate text file content"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            issues = []
            if 'notebooks' in file_path.parent.name:
                required = ['# Conversation Thread:', 'Date:', 'Participants:']
                missing = [req for req in required if req not in content]
                if missing:
                    issues.append(f"Missing required sections: {missing}")

            elif 'summaries' in file_path.parent.name:
                required = ['Key Points:', 'Statistics:']
                missing = [req for req in required if req not in content]
                if missing:
                    issues.append(f"Missing required sections: {missing}")

            return {
                'valid': len(issues) == 0,
                'issues': issues
            }

        except Exception as e:
            return {
                'valid': False,
                'issues': [str(e)]
            }

    def generate_report(self, results):
        """Generate HTML verification report"""
        self.logger.info("Generating verification report...")
        report_dir = self.base_dir / 'verification_reports'
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f'verification_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self._get_html_header())
                f.write(self._get_summary_table(results))
                f.write(self._get_detailed_results(results))
                f.write('</body></html>')
            
            self.logger.info(f"Generated report at: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return None

    def _get_html_header(self):
        return """
        <html>
        <head>
            <meta charset="utf-8">
            <title>Output Verification Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
                .summary-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .summary-table th, .summary-table td { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: left; 
                }
                .summary-table th { background: #f5f5f5; }
                .directory { margin: 20px 0; }
                .file { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
                .valid { background: #e6ffe6; }
                .invalid { background: #ffe6e6; }
                .path { font-family: monospace; }
                .issues { color: #cc0000; }
                .nav { position: sticky; top: 0; background: white; padding: 10px 0; }
            </style>
        </head>
        <body>
        """

    def _get_summary_table(self, results):
        html = f"""
        <h1>Output Verification Report</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Files: {results['total']}</p>
            <p>Valid Files: {results['valid']}</p>
            <p>Invalid Files: {results['invalid']}</p>
        </div>
        <table class="summary-table">
            <tr>
                <th>Directory</th>
                <th>Total Files</th>
                <th>Valid Files</th>
                <th>Invalid Files</th>
                <th>Status</th>
            </tr>
        """

        for dir_type, dir_results in results['by_type'].items():
            total = len(dir_results['files'])
            status = 'PASS' if dir_results['invalid'] == 0 else 'FAIL'
            status_color = 'green' if dir_results['invalid'] == 0 else 'red'
            
            html += f"""
            <tr>
                <td><a href="#{dir_type.replace('/', '_')}">{dir_type}</a></td>
                <td>{total}</td>
                <td>{dir_results['valid']}</td>
                <td>{dir_results['invalid']}</td>
                <td style="color: {status_color}">{status}</td>
            </tr>
            """
        
        html += "</table>"
        return html

    def _get_detailed_results(self, results):
        html = "<h2>Detailed Results</h2>"
        
        for dir_type, dir_results in results['by_type'].items():
            html += f"""
            <div class="directory" id="{dir_type.replace('/', '_')}">
                <h3>{dir_type}</h3>
            """
            
            for file_info in dir_results['files']:
                status_class = 'valid' if file_info['valid'] else 'invalid'
                html += f"""
                <div class="file {status_class}">
                    <h4>{file_info['name']}</h4>
                    <p class="path">Path: {file_info['path']}</p>
                    <p>Size: {file_info['size']} bytes</p>
                """
                
                if not file_info['valid']:
                    html += f"""
                    <div class="issues">
                        <p>Issues:</p>
                        <ul>
                        {''.join(f'<li>{issue}</li>' for issue in file_info['issues'])}
                        </ul>
                    </div>
                    """
                
                html += "</div>"
            
            html += "</div>"
        
        return html

def main():
    verifier = OutputVerifier()
    
    try:
        # Create example files if directory is empty
        if not any(verifier.output_dir.glob('**/*')):
            verifier.create_example_files()
        
        # Verify files and generate report
        results = verifier.verify_files()
        report_path = verifier.generate_report(results)
        
        if report_path and report_path.exists():
            # Open report in browser
            webbrowser.open(f'file://{os.path.abspath(report_path)}')
            
            # Check for coverage report
            coverage_path = verifier.base_dir / 'coverage_report' / 'index.html'
            if coverage_path.exists():
                webbrowser.open(f'file://{os.path.abspath(coverage_path)}')
            
            return 0 if results['invalid'] == 0 else 1
        else:
            verifier.logger.error("Failed to generate report")
            return 1
            
    except Exception as e:
        verifier.logger.error(f"Error running verification: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())