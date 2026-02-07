# Security & IAM Best Practices

## IAM Least Privilege
- Always use the principle of least privilege
- Create specific roles for specific tasks
- Avoid using wildcard (*) permissions
- Regularly audit IAM permissions with IAM Access Analyzer

## Credential Management
- Use IAM roles for EC2, Lambda, ECS instead of access keys
- Use AWS Secrets Manager for sensitive data
- Implement automatic key rotation
- Never hardcode credentials in scripts or code

## Example: Least Privilege S3 Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/app/*"
      ]
    }
  ]
}
```

## Network Security
- Use VPC endpoints for private AWS service access
- Enable VPC Flow Logs for network monitoring
- Use security groups and NACLs appropriately
- Implement AWS WAF for web applications

## Data Protection
- Enable encryption at rest (S3, RDS, EBS)
- Enable encryption in transit (SSL/TLS)
- Use KMS for key management
- Enable CloudTrail logging for audit trails

## Compliance & Auditing
- Regular security assessments
- Use AWS Config for compliance monitoring
- Enable AWS CloudTrail for all API calls
- Use Amazon GuardDuty for threat detection
