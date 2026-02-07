#!/usr/bin/env python3
"""
Service Mesh Analyzer - Analyze microservices communication patterns.
Evaluates service dependency graphs and communication efficiency.
"""

import json
from typing import Dict, List
from collections import defaultdict

class ServiceMeshAnalyzer:
    """Analyze microservices communication patterns."""
    
    def __init__(self):
        self.services = {}
        self.dependencies = defaultdict(list)
    
    def analyze_service_calls(self, trace_data: List[Dict]) -> Dict:
        """Analyze service-to-service calls."""
        call_patterns = defaultdict(lambda: {'count': 0, 'total_latency_ms': 0, 'errors': 0})
        
        for trace in trace_data:
            spans = trace.get('spans', [])
            
            for i, span in enumerate(spans):
                if i > 0:  # Look at child spans
                    parent_service = spans[i-1].get('service_name', 'unknown')
                    child_service = span.get('service_name', 'unknown')
                    
                    key = f'{parent_service} → {child_service}'
                    call_patterns[key]['count'] += 1
                    call_patterns[key]['total_latency_ms'] += span.get('duration_ms', 0)
                    
                    if span.get('status') == 'ERROR':
                        call_patterns[key]['errors'] += 1
        
        # Calculate averages
        for key in call_patterns:
            count = call_patterns[key]['count']
            call_patterns[key]['avg_latency_ms'] = round(
                call_patterns[key]['total_latency_ms'] / count if count > 0 else 0, 2
            )
            call_patterns[key]['error_rate_percent'] = round(
                (call_patterns[key]['errors'] / count * 100) if count > 0 else 0, 2
            )
        
        return dict(call_patterns)
    
    def detect_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies between services."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor) if neighbor in path else -1
                    if cycle_start != -1:
                        cycles.append(path[cycle_start:] + [neighbor])
            
            rec_stack.remove(node)
        
        # Find cycles
        for service in dependencies.keys():
            if service not in visited:
                dfs(service, [])
        
        return cycles
    
    def analyze_coupling(self, dependencies: Dict[str, List[str]]) -> Dict:
        """Analyze service coupling metrics."""
        # Count in-degree and out-degree
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        all_services = set(dependencies.keys())
        
        for service, deps in dependencies.items():
            out_degree[service] = len(deps)
            for dep in deps:
                in_degree[dep] += 1
                all_services.add(dep)
        
        # Calculate coupling metrics
        total_services = len(all_services)
        total_dependencies = sum(len(v) for v in dependencies.values())
        
        # Fan-out (services called by each service)
        high_fan_out = [
            {'service': s, 'fan_out': out_degree[s]}
            for s in all_services if out_degree[s] > 5
        ]
        
        # Fan-in (services that call a service)
        high_fan_in = [
            {'service': s, 'fan_in': in_degree[s]}
            for s in all_services if in_degree[s] > 5
        ]
        
        return {
            'total_services': total_services,
            'total_dependencies': total_dependencies,
            'average_dependencies_per_service': round(
                total_dependencies / total_services if total_services > 0 else 0, 2
            ),
            'high_fan_out_services': sorted(high_fan_out, key=lambda x: x['fan_out'], reverse=True)[:5],
            'high_fan_in_services': sorted(high_fan_in, key=lambda x: x['fan_in'], reverse=True)[:5],
            'coupling_metric': 'TIGHT' if total_dependencies > total_services * 2 else 'MODERATE' if total_dependencies > total_services else 'LOOSE'
        }
    
    def detect_chatty_interfaces(self, call_patterns: Dict) -> List[Dict]:
        """Detect services with chatty communication patterns."""
        chatty_patterns = []
        
        for pattern, metrics in call_patterns.items():
            count = metrics.get('count', 0)
            
            # Threshold: more than 100 calls in sample period
            if count > 100:
                chatty_patterns.append({
                    'pattern': pattern,
                    'call_count': count,
                    'avg_latency_ms': metrics['avg_latency_ms'],
                    'severity': 'HIGH' if count > 500 else 'MEDIUM',
                    'recommendation': 'Consider aggregating calls or batching requests'
                })
        
        return sorted(chatty_patterns, key=lambda x: x['call_count'], reverse=True)
    
    def identify_bottlenecks(self, call_patterns: Dict) -> List[Dict]:
        """Identify services that are bottlenecks."""
        bottlenecks = []
        
        # Group by called service
        services = defaultdict(lambda: {'count': 0, 'latency': []})
        
        for pattern, metrics in call_patterns.items():
            _, called_service = pattern.split(' → ')
            services[called_service]['count'] += metrics['count']
            services[called_service]['latency'].append(metrics['avg_latency_ms'])
        
        # Find high-traffic, high-latency services
        for service, data in services.items():
            avg_latency = sum(data['latency']) / len(data['latency']) if data['latency'] else 0
            
            if data['count'] > 500 and avg_latency > 100:
                bottlenecks.append({
                    'service': service,
                    'total_calls': data['count'],
                    'avg_latency_ms': round(avg_latency, 2),
                    'risk_level': 'CRITICAL' if data['count'] > 2000 else 'HIGH',
                    'recommendations': [
                        'Add caching layer',
                        'Implement rate limiting',
                        'Scale service horizontally',
                        'Optimize database queries'
                    ]
                })
        
        return sorted(bottlenecks, key=lambda x: x['total_calls'], reverse=True)
    
    def generate_service_mesh_report(self, trace_data: List[Dict], dependencies: Dict) -> Dict:
        """Generate comprehensive service mesh analysis report."""
        call_patterns = self.analyze_service_calls(trace_data)
        coupling = self.analyze_coupling(dependencies)
        cycles = self.detect_circular_dependencies(dependencies)
        chatty = self.detect_chatty_interfaces(call_patterns)
        bottlenecks = self.identify_bottlenecks(call_patterns)
        
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'summary': {
                'total_services': coupling['total_services'],
                'total_dependencies': coupling['total_dependencies'],
                'coupling_level': coupling['coupling_metric']
            },
            'call_patterns': call_patterns,
            'coupling_analysis': coupling,
            'circular_dependencies': cycles if cycles else 'none_detected',
            'chatty_interfaces': chatty,
            'bottlenecks': bottlenecks,
            'health_status': self.determine_health_status(cycles, chatty, bottlenecks),
            'recommendations': self.generate_recommendations(cycles, chatty, bottlenecks)
        }
    
    def determine_health_status(self, cycles, chatty, bottlenecks) -> str:
        if cycles:
            return 'CRITICAL'
        elif len(bottlenecks) > 3 or len(chatty) > 5:
            return 'WARNING'
        else:
            return 'HEALTHY'
    
    def generate_recommendations(self, cycles, chatty, bottlenecks) -> List[str]:
        recommendations = []
        
        if cycles:
            recommendations.append('CRITICAL: Eliminate circular dependencies')
        
        if len(bottlenecks) > 0:
            recommendations.append(f'Address {len(bottlenecks)} bottleneck services')
        
        if len(chatty) > 0:
            recommendations.append(f'Reduce chatty communication in {len(chatty)} patterns')
        
        recommendations.append('Implement API Gateway for external communication')
        recommendations.append('Use service mesh (Istio, Linkerd) for observability and resilience')
        
        return recommendations

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: service-mesh-analyzer.py <trace_data.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        trace_data = json.load(f)
    
    analyzer = ServiceMeshAnalyzer()
    report = analyzer.generate_service_mesh_report(
        trace_data.get('traces', []),
        trace_data.get('dependencies', {})
    )
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
