from datetime import datetime
import json

class AdvancedPatternDetector:
    def __init__(self):
        self._patterns = []
        self._analysis_complete = False

    def detect_patterns(self, threads_data):
        patterns = []
        
        for thread in threads_data:
            if not isinstance(thread, dict):
                continue
                
            thread_id = thread.get('thread_id', 'unknown')
            messages = thread.get('messages', [])
            metadata = thread.get('metadata', {})
            
            if len(messages) > 5:
                patterns.append({
                    "type": "active_discussion",
                    "confidence": 0.8,
                    "details": f"Thread {thread_id} contains {len(messages)} messages"
                })
            
            subject = metadata.get('subject', '')
            if subject and 'Re:' in subject:
                patterns.append({
                    "type": "conversation_thread",
                    "confidence": 0.9,
                    "details": f"Thread {thread_id} is part of an ongoing conversation"
                })
            
            participants = set(msg.get('from', '') for msg in messages if msg.get('from'))
            if len(participants) > 1:
                patterns.append({
                    "type": "multi_participant",
                    "confidence": 0.85,
                    "details": f"Thread {thread_id} involves {len(participants)} participants"
                })

        self._patterns = patterns
        self._analysis_complete = True

        # Save results for session validation
        try:
            with open('output/session_results.json', 'w') as f:
                json.dump({
                    'status': 'complete',
                    'patterns': patterns,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
        except Exception:
            pass

        return patterns