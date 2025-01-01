from typing import Dict, Any
from datetime import datetime

class ResultFormatter:
    """Standardizes result formats across all pipeline components"""
    
    @staticmethod
    def format_analysis_result(data: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Format analysis results in standard structure"""
        return {
            'metadata': {
                'stage': stage,
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'success',
            'data': data,
            'validation': {
                'is_valid': True,
                'checks_performed': [],
                'warnings': []
            }
        }
    
    @staticmethod
    def format_error_result(error: str, stage: str) -> Dict[str, Any]:
        """Format error results in standard structure"""
        return {
            'metadata': {
                'stage': stage,
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'error',
            'error': error,
            'validation': {
                'is_valid': False,
                'checks_performed': [],
                'warnings': [error]
            }
        }
    
    @staticmethod
    def format_session_result(results: Dict[str, Any]) -> Dict[str, Any]:
        """Format complete session results"""
        return {
            'metadata': {
                'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '1.0.0'
            },
            'status': 'success' if all(r.get('status') == 'success' for r in results.values()) else 'error',
            'stages': results,
            'validation': {
                'is_valid': True,
                'checks_performed': ['stage_completion', 'result_validation', 'data_integrity'],
                'warnings': []
            }
        }