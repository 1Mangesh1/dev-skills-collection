#!/usr/bin/env python3
"""
Bundle Analyzer - Analyze JavaScript/CSS bundle sizes.
Identifies large dependencies and optimization opportunities.
"""

import json
import subprocess
from typing import Dict, List
from pathlib import Path

class BundleAnalyzer:
    """Analyze application bundles."""
    
    def __init__(self):
        self.modules = {}
    
    def analyze_webpack_bundle(self, stats_file: str) -> Dict:
        """Analyze webpack bundle stats."""
        try:
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        except FileNotFoundError:
            return {"error": f"Stats file not found: {stats_file}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in stats file"}
        
        modules = stats.get('modules', [])
        total_size = 0
        by_type = {}
        
        # Analyze modules
        large_modules = []
        for module in modules:
            size = module.get('size', 0)
            total_size += size
            name = module.get('name', 'unknown')
            module_type = name.split('.')[-1] if '.' in name else 'unknown'
            
            if module_type not in by_type:
                by_type[module_type] = {'count': 0, 'total_size': 0}
            
            by_type[module_type]['count'] += 1
            by_type[module_type]['total_size'] += size
            
            # Track large modules
            if size > 100000:  # > 100KB
                large_modules.append({
                    'name': name,
                    'size_kb': round(size / 1024, 2),
                    'percentage': round((size / total_size) * 100, 2)
                })
        
        large_modules.sort(key=lambda x: x['size_kb'], reverse=True)
        
        return {
            'total_size_kb': round(total_size / 1024, 2),
            'module_count': len(modules),
            'by_type': {
                k: {
                    'count': v['count'],
                    'size_kb': round(v['total_size'] / 1024, 2)
                }
                for k, v in by_type.items()
            },
            'large_modules': large_modules[:10],
            'gzip_estimate_kb': round((total_size * 0.3) / 1024, 2),  # ~30% compression
            'brotli_estimate_kb': round((total_size * 0.25) / 1024, 2)  # ~25% compression
        }
    
    def analyze_npm_dependencies(self, package_file: str = 'package.json') -> Dict:
        """Analyze npm dependencies and their sizes."""
        try:
            with open(package_file, 'r') as f:
                package = json.load(f)
        except FileNotFoundError:
            return {"error": "package.json not found"}
        
        dependencies = package.get('dependencies', {})
        dev_dependencies = package.get('devDependencies', {})
        
        analysis = {
            'total_dependencies': len(dependencies),
            'total_dev_dependencies': len(dev_dependencies),
            'largest_dependencies': self.identify_heavy_packages(
                list(dependencies.keys())[:20]
            ),
            'unused_dependencies': self.find_unused_dependencies(package_file),
            'outdated_packages': self.check_outdated_packages()
        }
        
        return analysis
    
    def identify_heavy_packages(self, package_names: List[str]) -> List[Dict]:
        """Identify heavy npm packages."""
        # Approximate sizes of common heavy packages
        known_sizes = {
            'react': 39,
            'react-dom': 39,
            'lodash': 78,
            'moment': 67,
            'express': 51,
            'angular': 145,
            'vue': 33,
            'jquery': 85,
            'bootstrap': 50,
            'webpack': 85,
            'typescript': 43
        }
        
        heavy = []
        for pkg in package_names:
            if pkg in known_sizes:
                heavy.append({
                    'package': pkg,
                    'estimated_kb': known_sizes[pkg],
                    'recommendation': f"Consider {self.get_alternative(pkg)}"
                })
        
        return sorted(heavy, key=lambda x: x['estimated_kb'], reverse=True)[:5]
    
    def get_alternative(self, package: str) -> str:
        """Suggest package alternatives."""
        alternatives = {
            'moment': 'date-fns or dayjs (smaller)',
            'lodash': 'lodash-es with tree-shaking or native methods',
            'jquery': 'use native DOM methods',
            'react': 'preact (lighter alternative)'
        }
        return alternatives.get(package, "checking alternatives")
    
    def find_unused_dependencies(self, package_file: str) -> List[str]:
        """Identify potentially unused dependencies."""
        # This is a simplified implementation
        # In practice, use tools like depcheck
        return []
    
    def check_outdated_packages(self) -> List[str]:
        """Check for outdated packages."""
        # Use npm outdated
        return []
    
    def generate_bundle_report(self, stats_file: str) -> Dict:
        """Generate comprehensive bundle analysis report."""
        analysis = self.analyze_webpack_bundle(stats_file)
        
        if 'error' in analysis:
            return analysis
        
        total_kb = analysis['total_size_kb']
        
        # Generate recommendations
        recommendations = []
        
        if total_kb > 500:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Large JavaScript Bundle',
                'current': f'{total_kb}KB',
                'target': '200-300KB',
                'suggestions': [
                    'Implement code splitting by route',
                    'Use dynamic imports for heavy libraries',
                    'Remove unused dependencies',
                    'Tree-shake dead code'
                ]
            })
        
        if analysis['module_count'] > 100:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'High Module Count',
                'suggestions': [
                    'Merge small modules',
                    'Use bundle analysis tool',
                    'Review dependency tree'
                ]
            })
        
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'bundle_analysis': analysis,
            'compression': {
                'uncompressed_kb': total_kb,
                'gzip_kb': analysis['gzip_estimate_kb'],
                'brotli_kb': analysis['brotli_estimate_kb'],
                'gzip_savings_percent': round((1 - analysis['gzip_estimate_kb']/total_kb) * 100)
            },
            'recommendations': recommendations
        }

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: bundle-analyzer.py <stats.json>")
        sys.exit(1)
    
    analyzer = BundleAnalyzer()
    report = analyzer.generate_bundle_report(sys.argv[1])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
