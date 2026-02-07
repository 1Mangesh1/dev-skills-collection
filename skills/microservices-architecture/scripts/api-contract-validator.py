#!/usr/bin/env python3
"""
API Contract Validator - Validate service API contracts and compatibility.
Ensures services maintain backward compatibility and consistent interfaces.
"""

import json
from typing import Dict, List

class APIContractValidator:
    """Validate API contracts between services."""
    
    def __init__(self):
        self.schemas = {}
    
    def validate_openapi_spec(self, spec: Dict) -> Dict:
        """Validate OpenAPI specification."""
        issues = []
        
        # Check required OpenAPI fields
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                issues.append({
                    'severity': 'ERROR',
                    'field': field,
                    'message': f'Missing required field: {field}'
                })
        
        # Validate paths
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                
                # Check for required operation fields
                if 'responses' not in operation:
                    issues.append({
                        'severity': 'ERROR',
                        'path': f'{path}[{method}]',
                        'message': 'Missing responses object'
                    })
                
                # Check for operationId (useful for code generation)
                if 'operationId' not in operation:
                    issues.append({
                        'severity': 'WARNING',
                        'path': f'{path}[{method}]',
                        'message': 'Missing operationId (recommended for code generation)'
                    })
        
        return {
            'spec_version': spec.get('openapi', 'unknown'),
            'title': spec.get('info', {}).get('title', 'unknown'),
            'valid': len([i for i in issues if i['severity'] == 'ERROR']) == 0,
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def check_backward_compatibility(self, old_spec: Dict, new_spec: Dict) -> Dict:
        """Check if new spec is backward compatible with old."""
        incompatibilities = []
        
        old_paths = old_spec.get('paths', {})
        new_paths = new_spec.get('paths', {})
        
        # Check removed endpoints
        for path in old_paths:
            if path not in new_paths:
                incompatibilities.append({
                    'type': 'REMOVED_ENDPOINT',
                    'severity': 'CRITICAL',
                    'path': path,
                    'message': f'Endpoint {path} was removed'
                })
        
        # Check modified endpoints
        for path in old_paths:
            if path in new_paths:
                old_methods = old_paths[path]
                new_methods = new_paths[path]
                
                for method in old_methods:
                    if method not in new_methods:
                        incompatibilities.append({
                            'type': 'REMOVED_METHOD',
                            'severity': 'CRITICAL',
                            'endpoint': f'{path}[{method}]',
                            'message': f'Method {method} was removed'
                        })
                    else:
                        # Check parameters
                        old_params = old_methods[method].get('parameters', [])
                        new_params = new_methods[method].get('parameters', [])
                        
                        old_required = {
                            p['name'] for p in old_params if p.get('required', False)
                        }
                        new_required = {
                            p['name'] for p in new_params if p.get('required', False)
                        }
                        
                        # Check for new required parameters
                        added_required = new_required - old_required
                        if added_required:
                            incompatibilities.append({
                                'type': 'NEW_REQUIRED_PARAM',
                                'severity': 'CRITICAL',
                                'endpoint': f'{path}[{method}]',
                                'parameters': list(added_required),
                                'message': f'New required parameters: {added_required}'
                            })
        
        return {
            'compatible': len(incompatibilities) == 0,
            'incompatibilities': incompatibilities,
            'breaking_changes': len([i for i in incompatibilities if i['severity'] == 'CRITICAL'])
        }
    
    def validate_response_schema(self, response: Dict, schema: Dict) -> bool:
        """Validate response against schema."""
        # Simple validation - checks basic type matching
        if 'type' not in schema:
            return True
        
        schema_type = schema['type']
        value_type = type(response).__name__
        
        type_mapping = {
            'string': 'str',
            'number': ('float', 'int'),
            'integer': 'int',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict'
        }
        
        expected = type_mapping.get(schema_type)
        
        if isinstance(expected, tuple):
            return value_type in expected
        else:
            return expected == value_type
    
    def detect_api_drift(self, implemented_api: Dict, documented_api: Dict) -> List[Dict]:
        """Detect differences between implemented and documented API."""
        drift_issues = []
        
        impl_paths = implemented_api.get('paths', {})
        doc_paths = documented_api.get('paths', {})
        
        # Implemented but not documented
        for path in impl_paths:
            if path not in doc_paths:
                drift_issues.append({
                    'type': 'UNDOCUMENTED_ENDPOINT',
                    'severity': 'MEDIUM',
                    'path': path,
                    'message': f'Endpoint {path} exists but is not documented'
                })
        
        # Documented but not implemented
        for path in doc_paths:
            if path not in impl_paths:
                drift_issues.append({
                    'type': 'MISSING_ENDPOINT',
                    'severity': 'HIGH',
                    'path': path,
                    'message': f'Endpoint {path} is documented but not implemented'
                })
        
        return drift_issues
    
    def generate_contract_report(self, service_name: str, spec: Dict) -> Dict:
        """Generate API contract validation report."""
        validation = self.validate_openapi_spec(spec)
        
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'service': service_name,
            'spec_validation': validation,
            'endpoints': {
                'total': len(spec.get('paths', {})),
                'by_method': self._count_by_method(spec)
            },
            'recommendations': self._generate_recommendations(validation),
            'contract_quality_score': self._calculate_quality_score(validation)
        }
    
    def _count_by_method(self, spec: Dict) -> Dict:
        """Count endpoints by HTTP method."""
        counts = {}
        for path, methods in spec.get('paths', {}).items():
            for method in methods:
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    counts[method] = counts.get(method, 0) + 1
        return counts
    
    def _generate_recommendations(self, validation: Dict) -> List[str]:
        """Generate recommendations based on validation."""
        recommendations = []
        
        if not validation['valid']:
            recommendations.append('Fix specification errors')
        
        error_count = len([i for i in validation.get('issues', []) if i['severity'] == 'ERROR'])
        warning_count = len([i for i in validation.get('issues', []) if i['severity'] == 'WARNING'])
        
        if warning_count > 0:
            recommendations.append(f'Address {warning_count} warnings')
        
        recommendations.append('Use API versioning strategy (URL path vs header)')
        recommendations.append('Implement API gateway for cross-cutting concerns')
        recommendations.append('Enable API documentation with Swagger/OpenAPI')
        
        return recommendations
    
    def _calculate_quality_score(self, validation: Dict) -> int:
        """Calculate API contract quality score."""
        errors = len([i for i in validation.get('issues', []) if i['severity'] == 'ERROR'])
        warnings = len([i for i in validation.get('issues', []) if i['severity'] == 'WARNING'])
        
        score = 100 - (errors * 10 + warnings * 2)
        return max(0, score)

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: api-contract-validator.py <openapi_spec.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        spec = json.load(f)
    
    validator = APIContractValidator()
    report = validator.generate_contract_report("api-service", spec)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
