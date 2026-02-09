#!/usr/bin/env python3
"""
Dockerfile Linter - Analyze Dockerfiles for best practices.
Checks for security issues, performance, and optimization recommendations.
"""

import re
import json
from typing import List, Dict

class DockerfileLinter:
    """Lint Dockerfiles for best practices."""
    
    def __init__(self):
        self.issues = []
    
    def parse_dockerfile(self, filepath: str) -> List[str]:
        """Parse Dockerfile lines."""
        try:
            with open(filepath, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            return []
    
    def check_base_image(self, lines: List[str]) -> List[Dict]:
        """Check base image for best practices."""
        issues = []
        
        from_pattern = r'^FROM\s+(.+)$'
        
        for i, line in enumerate(lines, 1):
            match = re.match(from_pattern, line)
            if match:
                image = match.group(1).strip()
                
                # Check for latest tag
                if image.endswith(':latest') or ':' not in image:
                    issues.append({
                        'line': i,
                        'severity': 'HIGH',
                        'issue': 'Using latest or unspecified image tag',
                        'current': image,
                        'recommendation': 'Always use specific version tags for reproducibility',
                        'example': 'FROM python:3.11-slim'
                    })
                
                # Check for heavy base images
                if any(base in image for base in ['ubuntu', 'debian', 'centos']):
                    issues.append({
                        'line': i,
                        'severity': 'MEDIUM',
                        'issue': f'Using heavy base image: {image}',
                        'recommendation': 'Use slim/alpine variants for smaller images',
                        'example': 'FROM python:3.11-slim or python:3.11-alpine'
                    })
        
        return issues
    
    def check_user_privilege(self, lines: List[str]) -> List[Dict]:
        """Check if container runs as root."""
        issues = []
        
        user_defined = False
        for i, line in enumerate(lines, 1):
            if re.match(r'^USER\s+', line):
                user_match = re.match(r'^USER\s+(.+)$', line)
                if user_match:
                    user = user_match.group(1).strip()
                    if user != 'root':
                        user_defined = True
        
        if not user_defined:
            issues.append({
                'line': None,
                'severity': 'CRITICAL',
                'issue': 'Container runs as root user',
                'recommendation': 'Create and use a non-root user',
                'example': 'RUN useradd -r -u 1001 appuser\nUSER appuser'
            })
        
        return issues
    
    def check_layer_count(self, lines: List[str]) -> List[Dict]:
        """Check for inefficient layering."""
        issues = []
        
        run_count = len([l for l in lines if re.match(r'^RUN\s+', l)])
        
        if run_count > 10:
            issues.append({
                'severity': 'MEDIUM',
                'issue': f'Too many RUN instructions ({run_count})',
                'recommendation': 'Combine RUN commands with && to reduce layers',
                'impact': 'Each RUN creates a layer, increasing image size'
            })
        
        return issues
    
    def check_security_practices(self, lines: List[str]) -> List[Dict]:
        """Check for security vulnerabilities."""
        issues = []
        content = '\n'.join(lines)
        
        # Check for hardcoded secrets
        secret_patterns = {
            'password': r'password\s*=',
            'api_key': r'api[_-]?key\s*=',
            'secret': r'secret\s*=',
            'token': r'token\s*='
        }
        
        for secret_type, pattern in secret_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'severity': 'CRITICAL',
                    'issue': f'Potential {secret_type} hardcoded in Dockerfile',
                    'recommendation': 'Use build arguments or environment variables',
                    'example': 'ARG API_KEY\nENV API_KEY=$API_KEY'
                })
        
        # Check for apt-get without cleanup
        if 'apt-get install' in content and 'apt-get clean' not in content:
            issues.append({
                'severity': 'MEDIUM',
                'issue': 'apt-get used without cleanup',
                'recommendation': 'Clean apt cache to reduce image size',
                'example': 'RUN apt-get update && apt-get install -y ... && apt-get clean'
            })
        
        # Check for sudo usage
        if 'sudo' in content:
            issues.append({
                'severity': 'MEDIUM',
                'issue': 'sudo used in Dockerfile',
                'recommendation': 'Unnecessary in containers, use USER instead'
            })
        
        return issues
    
    def check_health_check(self, lines: List[str]) -> List[Dict]:
        """Check for HEALTHCHECK directive."""
        issues = []
        
        has_healthcheck = any(re.match(r'^HEALTHCHECK\s+', line) for line in lines)
        
        if not has_healthcheck:
            issues.append({
                'severity': 'MEDIUM',
                'issue': 'No HEALTHCHECK defined',
                'recommendation': 'Add health check for production readiness',
                'example': 'HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health'
            })
        
        return issues
    
    def check_entrypoint(self, lines: List[str]) -> List[Dict]:
        """Check ENTRYPOINT and CMD."""
        issues = []
        
        has_entrypoint = any(re.match(r'^ENTRYPOINT\s+', line) for line in lines)
        has_cmd = any(re.match(r'^CMD\s+', line) for line in lines)
        
        if not has_entrypoint and not has_cmd:
            issues.append({
                'severity': 'HIGH',
                'issue': 'No ENTRYPOINT or CMD defined',
                'recommendation': 'Define default command to run',
                'example': 'ENTRYPOINT ["python", "app.py"]'
            })
        
        return issues
    
    def lint_dockerfile(self, filepath: str) -> Dict:
        """Lint entire Dockerfile."""
        lines = self.parse_dockerfile(filepath)
        
        if not lines:
            return {'error': f'Could not read {filepath}'}
        
        all_issues = []
        all_issues.extend(self.check_base_image(lines))
        all_issues.extend(self.check_user_privilege(lines))
        all_issues.extend(self.check_layer_count(lines))
        all_issues.extend(self.check_security_practices(lines))
        all_issues.extend(self.check_health_check(lines))
        all_issues.extend(self.check_entrypoint(lines))
        
        # Categorize
        critical = []
        high = []
        medium = []
        for issue in all_issues:
            severity = issue.get('severity')
            if severity == 'CRITICAL':
                critical.append(issue)
            elif severity == 'HIGH':
                high.append(issue)
            elif severity == 'MEDIUM':
                medium.append(issue)
        
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'file': filepath,
            'total_issues': len(all_issues),
            'critical_issues': len(critical),
            'high_issues': len(high),
            'medium_issues': len(medium),
            'issues': sorted(all_issues, key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}.get(x.get('severity'), 3)),
            'score': max(0, 100 - (len(critical) * 20 + len(high) * 10 + len(medium) * 5))
        }

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: dockerfile-linter.py <Dockerfile>")
        sys.exit(1)
    
    linter = DockerfileLinter()
    report = linter.lint_dockerfile(sys.argv[1])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
