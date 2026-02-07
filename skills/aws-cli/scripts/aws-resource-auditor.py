#!/usr/bin/env python3
"""
AWS Resource Auditor - Scan AWS resources across regions for compliance and security
Usage: python3 aws-resource-auditor.py --profile <profile> --region <region>
"""

import json
import argparse
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any
from botocore.exceptions import ClientError

class AWSResourceAuditor:
    def __init__(self, profile: str = 'default', region: str = 'us-east-1'):
        """Initialize AWS session with specified profile and region"""
        session = boto3.Session(profile_name=profile, region_name=region)
        self.ec2 = session.client('ec2')
        self.s3 = session.client('s3')
        self.iam = session.client('iam')
        self.rds = session.client('rds')
        self.profile = profile
        self.region = region
        self.audit_report = {
            'timestamp': datetime.now().isoformat(),
            'profile': profile,
            'region': region,
            'findings': []
        }
    
    def audit_ec2_instances(self) -> List[Dict[str, Any]]:
        """Audit EC2 instances for security best practices"""
        findings = []
        
        try:
            response = self.ec2.describe_instances()
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    state = instance['State']['Name']
                    
                    # Check for public IP
                    if instance.get('PublicIpAddress'):
                        findings.append({
                            'severity': 'medium',
                            'resource_type': 'ec2',
                            'resource_id': instance_id,
                            'finding': f"Instance {instance_id} has public IP: {instance['PublicIpAddress']}",
                            'recommendation': 'Use NAT gateway or bastion host for private access'
                        })
                    
                    # Check monitoring enabled
                    monitoring = instance.get('Monitoring', {}).get('State', 'disabled')
                    if monitoring == 'disabled':
                        findings.append({
                            'severity': 'low',
                            'resource_type': 'ec2',
                            'resource_id': instance_id,
                            'finding': f"Detailed monitoring disabled for {instance_id}",
                            'recommendation': 'Enable CloudWatch detailed monitoring'
                        })
                    
                    # Check tags
                    tags = instance.get('Tags', [])
                    if not tags:
                        findings.append({
                            'severity': 'low',
                            'resource_type': 'ec2',
                            'resource_id': instance_id,
                            'finding': f"No tags found for instance {instance_id}",
                            'recommendation': 'Add Environment, Owner, and CostCenter tags'
                        })
        
        except ClientError as e:
            findings.append({
                'severity': 'error',
                'resource_type': 'ec2',
                'finding': f"Error auditing EC2: {e.response['Error']['Message']}",
                'recommendation': 'Check IAM permissions'
            })
        
        return findings
    
    def audit_s3_buckets(self) -> List[Dict[str, Any]]:
        """Audit S3 buckets for security configuration"""
        findings = []
        
        try:
            response = self.s3.list_buckets()
            
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                
                # Check public access block
                try:
                    pub_access = self.s3.get_public_access_block(Bucket=bucket_name)
                    config = pub_access['PublicAccessBlockConfiguration']
                    
                    if not all([
                        config['BlockPublicAcls'],
                        config['IgnorePublicAcls'],
                        config['BlockPublicPolicy'],
                        config['RestrictPublicBuckets']
                    ]):
                        findings.append({
                            'severity': 'high',
                            'resource_type': 's3',
                            'resource_id': bucket_name,
                            'finding': f"S3 bucket {bucket_name} has public access enabled",
                            'recommendation': 'Enable all public access blocks'
                        })
                
                except ClientError:
                    findings.append({
                        'severity': 'high',
                        'resource_type': 's3',
                        'resource_id': bucket_name,
                        'finding': f"No public access block configured for {bucket_name}",
                        'recommendation': 'Enable block public access'
                    })
                
                # Check versioning
                try:
                    versioning = self.s3.get_bucket_versioning(Bucket=bucket_name)
                    if versioning.get('Status') != 'Enabled':
                        findings.append({
                            'severity': 'medium',
                            'resource_type': 's3',
                            'resource_id': bucket_name,
                            'finding': f"S3 versioning not enabled for {bucket_name}",
                            'recommendation': 'Enable versioning for data recovery'
                        })
                except ClientError as e:
                    pass
        
        except ClientError as e:
            findings.append({
                'severity': 'error',
                'resource_type': 's3',
                'finding': f"Error auditing S3: {e.response['Error']['Message']}",
                'recommendation': 'Check IAM permissions'
            })
        
        return findings
    
    def audit_security_groups(self) -> List[Dict[str, Any]]:
        """Audit security group rules for overly permissive access"""
        findings = []
        
        try:
            response = self.ec2.describe_security_groups()
            
            for sg in response['SecurityGroups']:
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                for rule in sg['IpPermissions']:
                    # Check for 0.0.0.0/0 access
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            port = rule.get('FromPort', 'all')
                            protocol = rule.get('IpProtocol', 'all')
                            
                            findings.append({
                                'severity': 'high' if port in [22, 3389, 5432] else 'medium',
                                'resource_type': 'security_group',
                                'resource_id': sg_id,
                                'finding': f"Overly permissive rule in {sg_name}: {protocol}/{port} open to 0.0.0.0/0",
                                'recommendation': 'Restrict to specific IP ranges or security groups'
                            })
        
        except ClientError as e:
            findings.append({
                'severity': 'error',
                'resource_type': 'security_group',
                'finding': f"Error auditing security groups: {e.response['Error']['Message']}",
                'recommendation': 'Check IAM permissions'
            })
        
        return findings
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate complete audit report"""
        print(f"Auditing AWS resources in {self.region} (profile: {self.profile})...")
        
        self.audit_report['findings'].extend(self.audit_ec2_instances())
        self.audit_report['findings'].extend(self.audit_s3_buckets())
        self.audit_report['findings'].extend(self.audit_security_groups())
        
        # Summary
        self.audit_report['summary'] = {
            'total_findings': len(self.audit_report['findings']),
            'high_severity': len([f for f in self.audit_report['findings'] if f.get('severity') == 'high']),
            'medium_severity': len([f for f in self.audit_report['findings'] if f.get('severity') == 'medium']),
            'low_severity': len([f for f in self.audit_report['findings'] if f.get('severity') == 'low']),
            'errors': len([f for f in self.audit_report['findings'] if f.get('severity') == 'error'])
        }
        
        return self.audit_report

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Auditor')
    parser.add_argument('--profile', default='default', help='AWS profile to use')
    parser.add_argument('--region', default='us-east-1', help='AWS region to audit')
    parser.add_argument('--output', help='Output file for JSON report')
    
    args = parser.parse_args()
    
    auditor = AWSResourceAuditor(profile=args.profile, region=args.region)
    report = auditor.generate_report()
    
    # Print summary
    print("\n" + "="*50)
    print("AUDIT SUMMARY")
    print("="*50)
    print(json.dumps(report['summary'], indent=2))
    
    # Output findings
    if report['findings']:
        print("\nFINDINGS:")
        for finding in sorted(report['findings'], key=lambda x: {'high': 0, 'medium': 1, 'low': 2, 'error': 3}.get(x.get('severity'), 4)):
            print(f"  [{finding['severity'].upper()}] {finding['finding']}")
            print(f"    → {finding['recommendation']}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {args.output}")

if __name__ == '__main__':
    main()
