#!/usr/bin/env python3
"""
Performance Auditor - Analyze web performance metrics.
Evaluates Core Web Vitals, load times, and resource optimization.
"""

import json
import time
from typing import Dict, List
import subprocess

class PerformanceAuditor:
    """Audit web performance metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def measure_page_load(self, url: str, runs: int = 3) -> Dict:
        """Measure page load time using headless browser."""
        load_times = []
        
        try:
            # Using curl as simple alternative to headless browser
            for _ in range(runs):
                result = subprocess.run(
                    ['curl', '-w', '%{time_total}', '-o', '/dev/null', '-s', url],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    load_times.append(float(result.stdout))
        except FileNotFoundError:
            return {"error": "curl not installed"}
        except Exception as e:
            return {"error": str(e)}
        
        if not load_times:
            return {"error": "Failed to measure load time"}
        
        return {
            'url': url,
            'runs': runs,
            'measurements_seconds': load_times,
            'average_seconds': round(sum(load_times) / len(load_times), 3),
            'min_seconds': round(min(load_times), 3),
            'max_seconds': round(max(load_times), 3),
            'performance_grade': self.grade_load_time(
                sum(load_times) / len(load_times)
            )
        }
    
    def grade_load_time(self, load_time: float) -> str:
        """Grade performance based on load time."""
        if load_time < 1.0:
            return "A (Excellent)"
        elif load_time < 2.0:
            return "B (Good)"
        elif load_time < 3.0:
            return "C (Acceptable)"
        elif load_time < 5.0:
            return "D (Poor)"
        else:
            return "F (Critical)"
    
    def analyze_core_web_vitals(self, metrics: Dict) -> Dict:
        """Analyze Core Web Vitals (LCP, FID, CLS)."""
        # Largest Contentful Paint (target < 2.5s)
        lcp = metrics.get('lcp_ms', 0)
        lcp_status = 'GOOD' if lcp < 2500 else 'NEEDS_IMPROVEMENT' if lcp < 4000 else 'POOR'
        
        # First Input Delay (target < 100ms)
        fid = metrics.get('fid_ms', 0)
        fid_status = 'GOOD' if fid < 100 else 'NEEDS_IMPROVEMENT' if fid < 300 else 'POOR'
        
        # Cumulative Layout Shift (target < 0.1)
        cls = metrics.get('cls', 0.0)
        cls_status = 'GOOD' if cls < 0.1 else 'NEEDS_IMPROVEMENT' if cls < 0.25 else 'POOR'
        
        return {
            'lcp': {
                'value_ms': lcp,
                'target_ms': 2500,
                'status': lcp_status,
                'description': 'Largest Contentful Paint - how long before page looks fully rendered'
            },
            'fid': {
                'value_ms': fid,
                'target_ms': 100,
                'status': fid_status,
                'description': 'First Input Delay - responsiveness to user input'
            },
            'cls': {
                'value': cls,
                'target': 0.1,
                'status': cls_status,
                'description': 'Cumulative Layout Shift - visual stability'
            },
            'overall_score': self.calculate_cwv_score(lcp_status, fid_status, cls_status)
        }
    
    def calculate_cwv_score(self, lcp_status: str, fid_status: str, cls_status: str) -> int:
        """Calculate overall Core Web Vitals score."""
        statuses = [lcp_status, fid_status, cls_status]
        good_count = statuses.count('GOOD')
        
        if good_count == 3:
            return 100
        elif good_count == 2:
            return 75
        elif good_count == 1:
            return 50
        else:
            return 25
    
    def analyze_resource_timing(self, resources: List[Dict]) -> Dict:
        """Analyze resource loading performance."""
        if not resources:
            return {"error": "No resources provided"}
        
        # Group by resource type
        by_type = {}
        total_size = 0
        
        for resource in resources:
            res_type = resource.get('type', 'unknown')
            if res_type not in by_type:
                by_type[res_type] = {'count': 0, 'total_kb': 0, 'total_time_ms': 0}
            
            by_type[res_type]['count'] += 1
            kb = resource.get('size_bytes', 0) / 1024
            by_type[res_type]['total_kb'] += kb
            by_type[res_type]['total_time_ms'] += resource.get('load_time_ms', 0)
            total_size += kb
        
        # Find slowest resources
        slowest = sorted(resources, key=lambda x: x.get('load_time_ms', 0), reverse=True)[:5]
        
        return {
            'total_resources': len(resources),
            'total_size_kb': round(total_size, 2),
            'average_resource_size_kb': round(total_size / len(resources), 2),
            'by_type': {
                k: {
                    'count': v['count'],
                    'total_kb': round(v['total_kb'], 2),
                    'average_time_ms': round(v['total_time_ms'] / v['count'], 1)
                }
                for k, v in by_type.items()
            },
            'slowest_resources': [
                {
                    'name': r.get('name', ''),
                    'type': r.get('type'),
                    'size_kb': round(r.get('size_bytes', 0) / 1024, 2),
                    'load_time_ms': r.get('load_time_ms', 0)
                }
                for r in slowest
            ]
        }
    
    def detect_performance_issues(self, metrics: Dict) -> List[Dict]:
        """Detect common performance issues."""
        issues = []
        
        # Large bundle size
        if metrics.get('total_bundle_kb', 0) > 2000:
            issues.append({
                'severity': 'HIGH',
                'issue': 'Large JavaScript Bundle',
                'current': f"{metrics['total_bundle_kb']}KB",
                'recommendation': 'Code split and lazy load modules',
                'potential_savings_kb': metrics['total_bundle_kb'] - 1000
            })
        
        # High number of requests
        if metrics.get('total_requests', 0) > 50:
            issues.append({
                'severity': 'MEDIUM',
                'issue': 'Too Many Requests',
                'current': f"{metrics['total_requests']} requests",
                'recommendation': 'Consolidate resources, use CDN, enable HTTP/2'
            })
        
        # Unoptimized images
        if metrics.get('image_size_mb', 0) > metrics.get('total_size_mb', 1) * 0.4:
            issues.append({
                'severity': 'HIGH',
                'issue': 'Large Image Files',
                'recommendation': 'Use WebP format, optimize with tools like ImageMagick',
                'potential_savings_percent': 30
            })
        
        # Render-blocking resources
        if metrics.get('render_blocking_resources', 0) > 3:
            issues.append({
                'severity': 'MEDIUM',
                'issue': 'Render-Blocking Resources',
                'recommendation': 'Defer non-critical CSS/JS, use async/defer attributes'
            })
        
        return issues
    
    def generate_report(self, url: str, metrics: Dict) -> Dict:
        """Generate comprehensive performance report."""
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'url': url,
            'overall_score': metrics.get('overall_performance_score', 0),
            'core_web_vitals': self.analyze_core_web_vitals(metrics),
            'resource_analysis': self.analyze_resource_timing(metrics.get('resources', [])),
            'issues': self.detect_performance_issues(metrics),
            'recommendations': [
                'Implement caching strategies (browser, CDN, server)',
                'Enable compression (gzip, brotli)',
                'Minimize CSS/JavaScript bundle sizes',
                'Optimize images with modern formats',
                'Use a Content Delivery Network (CDN)',
                'Implement lazy loading for below-fold content',
                'Enable HTTP/2 and HTTP/3',
                'Use service workers for offline capability'
            ]
        }

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: performance-auditor.py <url>")
        sys.exit(1)
    
    auditor = PerformanceAuditor()
    
    # Example: Basic page load measurement
    url = sys.argv[1]
    result = auditor.measure_page_load(url)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
