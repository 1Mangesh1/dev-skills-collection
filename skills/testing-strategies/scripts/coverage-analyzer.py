#!/usr/bin/env python3
"""
Test Coverage Analyzer - Calculate and report code coverage metrics.
Analyzes test coverage and identifies untested code paths.
"""

import json
import re
from typing import Dict, List
from pathlib import Path

class CoverageAnalyzer:
    """Analyze test coverage metrics."""
    
    def __init__(self):
        self.coverage_data = {}
        self.total_lines = 0
        self.covered_lines = 0
    
    def parse_coverage_file(self, filepath: str) -> Dict:
        """Parse coverage report (supports coverage.py JSON format)."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_coverage_percentage(self, covered: int, total: int) -> float:
        """Calculate coverage percentage."""
        if total == 0:
            return 0.0
        return round((covered / total) * 100, 2)
    
    def analyze_file_coverage(self, filepath: str, coverage_data: Dict) -> Dict:
        """Analyze coverage for a specific file."""
        file_coverage = coverage_data.get(filepath, {})
        
        if not isinstance(file_coverage, dict):
            return {"error": f"Invalid coverage data for {filepath}"}
        
        executed_lines = file_coverage.get('executed_lines', [])
        missing_lines = file_coverage.get('missing_lines', [])
        
        total_lines = len(executed_lines) + len(missing_lines)
        coverage_pct = self.calculate_coverage_percentage(
            len(executed_lines), total_lines
        )
        
        return {
            'file': filepath,
            'total_lines': total_lines,
            'covered_lines': len(executed_lines),
            'missing_lines': len(missing_lines),
            'coverage_percent': coverage_pct,
            'coverage_grade': self.get_coverage_grade(coverage_pct),
            'uncovered_line_ranges': self.group_missing_lines(missing_lines)
        }
    
    def group_missing_lines(self, missing_lines: List[int]) -> List[str]:
        """Group consecutive missing lines into ranges."""
        if not missing_lines:
            return []
        
        missing_lines = sorted(set(missing_lines))
        ranges = []
        start = missing_lines[0]
        end = missing_lines[0]
        
        for line in missing_lines[1:]:
            if line == end + 1:
                end = line
            else:
                ranges.append(f"{start}-{end}" if start != end else str(start))
                start = end = line
        
        ranges.append(f"{start}-{end}" if start != end else str(start))
        return ranges
    
    def get_coverage_grade(self, percentage: float) -> str:
        """Get letter grade for coverage percentage."""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def find_untested_functions(self, source_file: str, coverage_data: Dict) -> List[Dict]:
        """Identify entirely uncovered functions."""
        untested_functions = []
        
        try:
            with open(source_file, 'r') as f:
                source_code = f.read()
            
            # Simple regex to find functions (Python)
            function_pattern = r'^def\s+(\w+)\s*\('
            missing_lines = set(coverage_data.get('missing_lines', []))
            
            current_line = 0
            for line in source_code.split('\n'):
                current_line += 1
                match = re.match(function_pattern, line)
                
                if match:
                    func_name = match.group(1)
                    # Check if function definition line is uncovered
                    if current_line in missing_lines:
                        untested_functions.append({
                            'function': func_name,
                            'line': current_line,
                            'type': 'uncovered_definition'
                        })
        except Exception as e:
            pass
        
        return untested_functions
    
    def identify_coverage_gaps(self, coverage_data: Dict) -> List[Dict]:
        """Identify modules with low coverage."""
        gaps = []
        
        for module, data in coverage_data.items():
            if isinstance(data, dict):
                covered = len(data.get('executed_lines', []))
                missing = len(data.get('missing_lines', []))
                total = covered + missing
                
                if total > 0:
                    coverage = (covered / total) * 100
                    if coverage < 70:
                        gaps.append({
                            'module': module,
                            'coverage_percent': round(coverage, 2),
                            'covered_lines': covered,
                            'missing_lines': missing,
                            'priority': 'high' if coverage < 50 else 'medium'
                        })
        
        return sorted(gaps, key=lambda x: x['coverage_percent'])
    
    def generate_coverage_report(self, coverage_file: str) -> Dict:
        """Generate comprehensive coverage report."""
        coverage_data = self.parse_coverage_file(coverage_file)
        
        if 'error' in coverage_data:
            return coverage_data
        
        # Calculate overall coverage
        total_covered = 0
        total_lines = 0
        
        file_analyses = []
        for filepath in coverage_data:
            if isinstance(coverage_data[filepath], dict):
                analysis = self.analyze_file_coverage(filepath, coverage_data)
                file_analyses.append(analysis)
                total_covered += analysis.get('covered_lines', 0)
                total_lines += analysis.get('total_lines', 0)
        
        overall_coverage = self.calculate_coverage_percentage(total_covered, total_lines)
        
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'overall_coverage': {
                'percent': overall_coverage,
                'grade': self.get_coverage_grade(overall_coverage),
                'total_lines': total_lines,
                'covered_lines': total_covered,
                'missing_lines': total_lines - total_covered
            },
            'files': file_analyses,
            'gaps': self.identify_coverage_gaps(coverage_data),
            'recommendations': self.get_recommendations(overall_coverage),
            'trend': {
                'status': 'improving' if overall_coverage > 65 else 'needs_improvement',
                'target': 80,
                'gap_to_target': max(0, 80 - overall_coverage)
            }
        }
    
    def get_recommendations(self, coverage: float) -> List[str]:
        """Get recommendations based on coverage percentage."""
        recommendations = []
        
        if coverage < 50:
            recommendations.append("Critical: Less than 50% coverage. Add unit tests for critical paths.")
        elif coverage < 70:
            recommendations.append("Add tests for commonly used modules (70% target).")
        elif coverage < 80:
            recommendations.append("Target 80% coverage. Focus on edge cases and error handling.")
        elif coverage < 90:
            recommendations.append("Test complex functions and integration scenarios.")
        else:
            recommendations.append("Maintain current coverage level. Add tests for new code.")
        
        recommendations.append("Use code coverage tools in CI/CD to prevent regression.")
        recommendations.append("Focus on testing high-risk areas first.")
        
        return recommendations

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: coverage-analyzer.py <coverage_file>")
        sys.exit(1)
    
    analyzer = CoverageAnalyzer()
    report = analyzer.generate_coverage_report(sys.argv[1])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
