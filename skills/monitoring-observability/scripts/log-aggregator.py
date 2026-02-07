#!/usr/bin/env python3
"""
Log Aggregator - Parse and analyze application logs.
Aggregates logs from multiple sources and identifies issues.
"""

import json
import re
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

class LogAggregator:
    """Aggregate and analyze logs."""
    
    def __init__(self):
        self.logs = []
        self.error_counts = defaultdict(int)
        self.warning_counts = defaultdict(int)
    
    def parse_json_log(self, log_line: str) -> Dict:
        """Parse JSON formatted log line."""
        try:
            return json.loads(log_line)
        except json.JSONDecodeError:
            return None
    
    def parse_text_log(self, log_line: str) -> Dict:
        """Parse text formatted log line."""
        # Example: [2024-02-07 10:30:45] ERROR: Database connection failed
        pattern = r'\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]\s(\w+):\s(.+)'
        match = re.match(pattern, log_line)
        
        if match:
            return {
                "timestamp": match.group(1),
                "level": match.group(2),
                "message": match.group(3)
            }
        return None
    
    def parse_log_file(self, filepath: str) -> List[Dict]:
        """Parse log file and extract structured logs."""
        logs = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    # Try JSON first
                    log = self.parse_json_log(line.strip())
                    if log is None:
                        log = self.parse_text_log(line.strip())
                    
                    if log:
                        logs.append(log)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
        
        return logs
    
    def extract_errors(self, logs: List[Dict]) -> List[Dict]:
        """Extract error logs."""
        return [log for log in logs if log.get('level') == 'ERROR']
    
    def extract_warnings(self, logs: List[Dict]) -> List[Dict]:
        """Extract warning logs."""
        return [log for log in logs if log.get('level') == 'WARNING']
    
    def count_by_level(self, logs: List[Dict]) -> Dict:
        """Count logs by severity level."""
        counts = defaultdict(int)
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            counts[level] += 1
        return dict(counts)
    
    def count_by_message_pattern(self, logs: List[Dict]) -> Dict:
        """Identify recurring error patterns."""
        patterns = defaultdict(int)
        for log in logs:
            message = log.get('message', '').lower()
            # Extract first 50 chars as pattern
            pattern = message[:50]
            patterns[pattern] += 1
        
        # Return top patterns only
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def detect_anomalies(self, logs: List[Dict]) -> Dict:
        """Detect anomalies in logs."""
        errors = self.extract_errors(logs)
        error_rate = (len(errors) / len(logs) * 100) if logs else 0
        
        anomalies = {
            "error_rate_percent": round(error_rate, 2),
            "threshold_exceeded": error_rate > 10,
            "total_errors": len(errors),
            "recent_errors": errors[-5:] if errors else []
        }
        
        return anomalies
    
    def generate_report(self, filepath: str) -> Dict:
        """Generate comprehensive log analysis report."""
        logs = self.parse_log_file(filepath)
        
        if not logs:
            return {"error": "No logs parsed"}
        
        return {
            "summary": {
                "total_logs": len(logs),
                "by_level": self.count_by_level(logs),
                "error_rate_percent": round((len(self.extract_errors(logs)) / len(logs) * 100), 2)
            },
            "errors": {
                "count": len(self.extract_errors(logs)),
                "samples": [log.get('message', '') for log in self.extract_errors(logs)[:5]]
            },
            "warnings": {
                "count": len(self.extract_warnings(logs))
            },
            "patterns": self.count_by_message_pattern(logs),
            "anomalies": self.detect_anomalies(logs)
        }

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: log-aggregator.py <logfile>")
        sys.exit(1)
    
    aggregator = LogAggregator()
    report = aggregator.generate_report(sys.argv[1])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
