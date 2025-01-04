from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

class PartialReportGenerator:
    def __init__(self, session_dir: Path):
        self.session_dir = Path(session_dir)
        self.reports_dir = self.session_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def generate_stage_report(self, stage: str, data: Dict[str, Any]) -> Path:
        report_file = self.reports_dir / f"{stage}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'stage': stage,
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(stage, data),
            'data': data
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report_file
        
    def _generate_summary(self, stage: str, data: Dict[str, Any]) -> Dict[str, Any]:
        summaries = {
            'document_processing': self._summarize_documents,
            'thread_analysis': self._summarize_threads,
            'pattern_detection': self._summarize_patterns,
            'timeline_generation': self._summarize_timeline
        }
        
        if stage in summaries:
            return summaries[stage](data)
        return {}
        
    def _summarize_documents(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'total_documents': len(data.get('documents', [])),
            'processed_pages': sum(doc.get('pages', 0) for doc in data.get('documents', [])),
            'extraction_status': data.get('status')
        }
        
    def _summarize_threads(self, data: Dict[str, Any]) -> Dict[str, Any]:
        threads = data.get('threads', [])
        return {
            'total_threads': len(threads),
            'avg_thread_length': sum(len(t.get('messages', [])) for t in threads) / len(threads) if threads else 0,
            'participant_count': len(set(p for t in threads for p in t.get('participants', [])))
        }
        
    def _summarize_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        patterns = data.get('patterns', {})
        return {
            'pattern_types': list(patterns.keys()),
            'significant_patterns': len([p for p in patterns.values() if p.get('significance', 0) > 0.7])
        }
        
    def _summarize_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'time_range': data.get('time_range'),
            'event_count': len(data.get('events', [])),
            'cluster_count': len(data.get('clusters', []))
        }
        
    def finalize_partial_reports(self) -> Path:
        summary_file = self.reports_dir / f"session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        reports = []
        for report in self.reports_dir.glob('*_report_*.json'):
            with open(report) as f:
                reports.append(json.load(f))
                
        summary = {
            'timestamp': datetime.now().isoformat(),
            'completed_stages': [r['stage'] for r in reports],
            'stage_summaries': {r['stage']: r['summary'] for r in reports}
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        return summary_file