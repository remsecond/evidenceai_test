import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import sys
from .checkpoint_manager import CheckpointManager

class CheckpointReporter:
    """Generates detailed reports about checkpoint status and history"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parents[2]
        self.checkpoint_manager = CheckpointManager(self.base_dir)
        self.output_dir = self.base_dir / "output" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_full_report(self) -> Path:
        """Generate comprehensive checkpoint report"""
        report_sections = []
        
        # Overall Status
        report_sections.extend([
            "# EvidenceAI Checkpoint Status Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overall Status",
            self._generate_overall_status(),
            "",
            "## Stage Details",
            self._generate_stage_details(),
            "",
            "## Checkpoint Chain Analysis",
            self._generate_chain_analysis(),
            "",
            "## Data Integrity Report",
            self._generate_integrity_report(),
            "",
            "## Recommendations",
            self._generate_recommendations()
        ])
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"checkpoint_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_sections))
            
        return report_file
        
    def _generate_overall_status(self) -> str:
        """Generate overall status section"""
        valid_files, invalid_files = self.checkpoint_manager.verify_all_checkpoints()
        
        status_lines = [
            f"- Total Checkpoints: {len(valid_files) + len(invalid_files)}",
            f"- Valid Checkpoints: {len(valid_files)}",
            f"- Invalid/Corrupted: {len(invalid_files)}",
            "",
            "### Stage Progress",
        ]
        
        # Add stage progress
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            status = self.checkpoint_manager.get_stage_status(stage)
            emoji = "✅" if status['status'] != 'not_started' else "⏳"
            status_lines.append(f"- {emoji} {stage.upper()}: {status['status']}")
            if status['status'] != 'not_started':
                status_lines.append(f"  - Last Updated: {status['last_updated']}")
                status_lines.append(f"  - Checkpoints: {status['checkpoint_count']}")
        
        return '\n'.join(status_lines)
        
    def _generate_stage_details(self) -> str:
        """Generate detailed stage information"""
        stage_lines = []
        
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            stage_lines.extend([
                f"### {stage.upper()}",
                ""
            ])
            
            status = self.checkpoint_manager.get_stage_status(stage)
            if status['status'] == 'not_started':
                stage_lines.append("Stage not started.")
                continue
                
            chain = self.checkpoint_manager.get_chain_of_checkpoints(stage)
            
            # Stage statistics
            stage_lines.extend([
                "#### Statistics",
                f"- Total Checkpoints: {len(chain)}",
                f"- Chain Complete: {'Yes' if status['chain_complete'] else 'No'}",
                f"- Latest Update: {status['last_updated']}",
                "",
                "#### Checkpoint History"
            ])
            
            # Add checkpoint history
            for cp in chain:
                stage_lines.extend([
                    f"- Checkpoint {cp['checkpoint_id']}:",
                    f"  - Time: {cp['timestamp']}",
                    f"  - Metadata: {json.dumps(cp['metadata'], indent=2)}"
                ])
            
            stage_lines.append("")
        
        return '\n'.join(stage_lines)
        
    def _generate_chain_analysis(self) -> str:
        """Generate analysis of checkpoint chains"""
        chain_lines = []
        
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            chain = self.checkpoint_manager.get_chain_of_checkpoints(stage)
            if not chain:
                continue
                
            chain_lines.extend([
                f"### {stage.upper()} Chain",
                f"Chain Length: {len(chain)}",
                ""
            ])
            
            # Analyze chain integrity
            broken_links = []
            for i in range(1, len(chain)):
                if chain[i]['previous_checkpoint'] != chain[i-1]['checkpoint_id']:
                    broken_links.append(i)
            
            if broken_links:
                chain_lines.append("⚠️ Chain Integrity Issues Detected:")
                for link in broken_links:
                    chain_lines.append(f"- Break between checkpoints {link} and {link+1}")
            else:
                chain_lines.append("✅ Chain Integrity Verified")
            
            chain_lines.append("")
            
        return '\n'.join(chain_lines)
        
    def _generate_integrity_report(self) -> str:
        """Generate data integrity report"""
        valid_files, invalid_files = self.checkpoint_manager.verify_all_checkpoints()
        
        integrity_lines = [
            "### Checkpoint Verification Results",
            f"- Valid Checkpoints: {len(valid_files)}",
            f"- Invalid Checkpoints: {len(invalid_files)}",
            ""
        ]
        
        if invalid_files:
            integrity_lines.extend([
                "### Invalid Checkpoints Detected:",
                ""
            ])
            
            for file in invalid_files:
                integrity_lines.append(f"- {file.name}")
                try:
                    with open(file) as f:
                        data = json.load(f)
                    integrity_lines.append(f"  - Stage: {data.get('stage', 'unknown')}")
                    integrity_lines.append(f"  - Time: {data.get('timestamp', 'unknown')}")
                except:
                    integrity_lines.append("  - Unable to read file")
                    
        return '\n'.join(integrity_lines)
        
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on checkpoint analysis"""
        recommendations = []
        
        # Check stage progression
        incomplete_stages = []
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            status = self.checkpoint_manager.get_stage_status(stage)
            if status['status'] == 'not_started':
                incomplete_stages.append(stage)
                
        if incomplete_stages:
            recommendations.extend([
                "### Stage Progression",
                f"- Complete {', '.join(incomplete_stages)} stages",
                ""
            ])
            
        # Check checkpoint frequency
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            chain = self.checkpoint_manager.get_chain_of_checkpoints(stage)
            if len(chain) > 10:
                recommendations.extend([
                    f"### {stage.upper()} Checkpoints",
                    "- Consider pruning old checkpoints to maintain performance",
                    f"- Current count: {len(chain)}",
                    ""
                ])
                
        # Check chain integrity
        broken_chains = []
        for stage in ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']:
            status = self.checkpoint_manager.get_stage_status(stage)
            if status['status'] != 'not_started' and not status['chain_complete']:
                broken_chains.append(stage)
                
        if broken_chains:
            recommendations.extend([
                "### Chain Integrity",
                "- Repair broken checkpoint chains in stages:",
                *[f"  - {stage}" for stage in broken_chains],
                ""
            ])
            
        return '\n'.join(recommendations)

def main():
    """Generate checkpoint report from command line"""
    reporter = CheckpointReporter()
    report_file = reporter.generate_full_report()
    print(f"\nReport generated: {report_file}")

if __name__ == "__main__":
    main()