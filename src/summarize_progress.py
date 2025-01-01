import json
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, List, Optional
from collections import defaultdict

class ProgressAnalyzer:
    """Analyzes development progress across sessions"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.checkpoint_dir = self.base_dir / "output" / "checkpoints"
        self.output_dir = self.base_dir / "output"
    
    def analyze_progress(self) -> Dict:
        """Analyze all checkpoints and generate progress summary"""
        checkpoints = self._load_checkpoints()
        if not checkpoints:
            return self._create_empty_summary()
            
        return {
            'checkpoint_summary': self._summarize_checkpoints(checkpoints),
            'stage_progress': self._analyze_stages(checkpoints),
            'time_analysis': self._analyze_timing(checkpoints),
            'recommendations': self._generate_recommendations(checkpoints),
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_checkpoints(self) -> List[Dict]:
        """Load all checkpoint files"""
        checkpoints = []
        for file in self.checkpoint_dir.glob("*_*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    checkpoints.append({
                        'file': file,
                        'stage': file.name.split('_')[0],
                        'timestamp': datetime.fromtimestamp(file.stat().st_mtime),
                        'data': data
                    })
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
        
        return sorted(checkpoints, key=lambda x: x['timestamp'])
    
    def _summarize_checkpoints(self, checkpoints: List[Dict]) -> Dict:
        """Create summary of checkpoint status"""
        stages = defaultdict(list)
        for cp in checkpoints:
            stages[cp['stage']].append(cp)
            
        return {
            'total_checkpoints': len(checkpoints),
            'stages_found': list(stages.keys()),
            'last_checkpoint': checkpoints[-1]['file'].name if checkpoints else None,
            'last_stage': checkpoints[-1]['stage'] if checkpoints else None,
            'stage_counts': {stage: len(cps) for stage, cps in stages.items()},
            'first_checkpoint_time': checkpoints[0]['timestamp'].isoformat() if checkpoints else None,
            'last_checkpoint_time': checkpoints[-1]['timestamp'].isoformat() if checkpoints else None
        }
    
    def _analyze_stages(self, checkpoints: List[Dict]) -> Dict:
        """Analyze progress through pipeline stages"""
        stages = defaultdict(list)
        stage_sequence = ['setup', 'pdf_parsing', 'threading', 'analysis', 'final']
        
        for cp in checkpoints:
            stages[cp['stage']].append(cp)
            
        completed_stages = []
        current_stage = None
        pending_stages = []
        
        for stage in stage_sequence:
            if stage in stages:
                if stage == checkpoints[-1]['stage']:
                    current_stage = stage
                elif stages[stage]:
                    completed_stages.append(stage)
                else:
                    pending_stages.append(stage)
                    
        return {
            'completed': completed_stages,
            'current': current_stage,
            'pending': pending_stages,
            'completion_percentage': (len(completed_stages) / len(stage_sequence)) * 100
        }
    
    def _analyze_timing(self, checkpoints: List[Dict]) -> Dict:
        """Analyze timing patterns between checkpoints"""
        if len(checkpoints) < 2:
            return {}
            
        intervals = []
        for i in range(1, len(checkpoints)):
            interval = (checkpoints[i]['timestamp'] - checkpoints[i-1]['timestamp']).total_seconds()
            intervals.append(interval)
            
        return {
            'average_interval': sum(intervals) / len(intervals),
            'min_interval': min(intervals),
            'max_interval': max(intervals),
            'total_development_time': sum(intervals)
        }
    
    def _generate_recommendations(self, checkpoints: List[Dict]) -> List[str]:
        """Generate recommendations based on checkpoint analysis"""
        recommendations = []
        stage_progress = self._analyze_stages(checkpoints)
        
        # Check stage completion
        if not stage_progress['completed']:
            recommendations.append("Begin with initial setup and PDF parsing stages")
        elif stage_progress['completion_percentage'] < 50:
            recommendations.append("Focus on completing core processing stages before optimization")
        
        # Check timing patterns
        timing = self._analyze_timing(checkpoints)
        if timing.get('average_interval', 0) > 3600:  # 1 hour
            recommendations.append("Consider more frequent checkpoints for better progress tracking")
        
        # Check stage balance
        summary = self._summarize_checkpoints(checkpoints)
        if max(summary['stage_counts'].values()) > 3 * min(summary['stage_counts'].values()):
            recommendations.append("Some stages have significantly more checkpoints - consider balancing development focus")
        
        return recommendations
    
    def _create_empty_summary(self) -> Dict:
        """Create summary structure for empty/new project"""
        return {
            'checkpoint_summary': {
                'total_checkpoints': 0,
                'stages_found': [],
                'last_checkpoint': None,
                'last_stage': None,
                'stage_counts': {},
                'first_checkpoint_time': None,
                'last_checkpoint_time': None
            },
            'stage_progress': {
                'completed': [],
                'current': None,
                'pending': ['setup', 'pdf_parsing', 'threading', 'analysis', 'final'],
                'completion_percentage': 0
            },
            'time_analysis': {},
            'recommendations': ["Start with initial setup and create first checkpoint"],
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self) -> None:
        """Generate detailed progress report"""
        summary = self.analyze_progress()
        
        # Format report
        report = [
            "# EvidenceAI Development Progress Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Checkpoint Summary",
            f"- Total Checkpoints: {summary['checkpoint_summary']['total_checkpoints']}",
            f"- Last Checkpoint: {summary['checkpoint_summary']['last_checkpoint']}",
            f"- Last Stage: {summary['checkpoint_summary']['last_stage']}",
            "",
            "## Stage Progress",
            f"- Completed Stages: {', '.join(summary['stage_progress']['completed']) or 'None'}",
            f"- Current Stage: {summary['stage_progress']['current'] or 'None'}",
            f"- Pending Stages: {', '.join(summary['stage_progress']['pending']) or 'None'}",
            f"- Completion: {summary['stage_progress']['completion_percentage']:.1f}%",
            "",
            "## Time Analysis",
        ]
        
        if summary['time_analysis']:
            report.extend([
                f"- Average Interval: {summary['time_analysis']['average_interval']/3600:.1f} hours",
                f"- Total Development Time: {summary['time_analysis']['total_development_time']/3600:.1f} hours"
            ])
            
        report.extend([
            "",
            "## Recommendations",
            *[f"- {rec}" for rec in summary['recommendations']]
        ])
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"progress_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))
            
        print(f"\nProgress report generated: {report_file}")

if __name__ == "__main__":
    analyzer = ProgressAnalyzer()
    analyzer.generate_report()