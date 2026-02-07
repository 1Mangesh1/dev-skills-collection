# AWS CLI Best Practices Guide

## Overview
The AWS CLI is a unified tool to manage AWS services from the command line. This guide covers best practices for authentication, security, and efficient usage.

## 1. Authentication & Profile Management

### Using Named Profiles
```bash
# Configure a new profile
aws configure --profile production
# Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY when prompted

# Use profile in commands
aws s3 ls --profile production

# Set default profile
export AWS_PROFILE=production
```

### MFA Device Configuration
```bash
# Configure MFA
aws iam enable-mfa-device --user-name $(aws iam get-user --query 'User.UserName' --output text) \
  --serial-number arn:aws:iam::123456789012:mfa/username \
  --authentication-code1 123456 \
  --authentication-code2 654321

# Assume role with MFA
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/production-role \
  --role-session-name prod-session \
  --serial-number arn:aws:iam::123456789012:mfa/username \
  --token-code 123456
```

### Using AWS SSO
```bash
# Configure SSO
aws configure sso
# Enter organization portal URL and region

# Login to SSO
aws sso login --profile my-sso-profile

# List available accounts
aws sso list-accounts --access-token <token>
```

## 2. Security Best Practices

### Credential Rotation
- Rotate access keys every 90 days
- Always use IAM users, never the root account
- Use temporary credentials via STS when possible
- Never commit credentials to version control

### Environment Variables for Scripts
```bash
# Use temporary credentials
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION="us-east-1"

# Verify credentials
aws sts get-caller-identity
```

### Audit and Monitor CLI Usage
```bash
# Enable CloudTrail to log all API calls
aws cloudtrail create-trail --name cli-audit --s3-bucket-name my-audit-logs

# Query CloudTrail logs
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=my-instance
```

## 3. Output Formatting

### JSON Output
```bash
# Default JSON output
aws ec2 describe-instances --output json

# Query specific fields
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table

# Pretty print
aws ec2 describe-instances | jq '.'
```

### JMESPath Queries
```bash
# Filter and extract data
aws ec2 describe-instances \
  --query 'Reservations[?Instances[?State.Name==`running`]].Instances[].[InstanceId,InstanceType,PublicIpAddress]' \
  --output table

# List all running instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

### CSV Export
```bash
# Export to CSV
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime]' \
  --output text | column -t > instances.csv

# Export with headers
echo "InstanceId,Type,LaunchTime" > instances.csv
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime]' --output text >> instances.csv
```

## 4. Batch Operations

### Process Multiple Resources
```bash
# Get all instances and iterate
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text | \
  xargs -I {} aws ec2 describe-instances --instance-ids {} --query 'Reservations[0].Instances[0].[InstanceId,State.Name]'

# Tag all instances
for instance_id in $(aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text); do
  aws ec2 create-tags --resources "$instance_id" --tags Key=Environment,Value=production
done
```

### S3 Batch Operations
```bash
# Sync directory
aws s3 sync ./local-dir s3://my-bucket/remote-path --delete

# Copy with metadata
aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/file.txt \
  --metadata "department=engineering,updated=$(date +%s)"

# List all objects
aws s3api list-objects-v2 --bucket my-bucket --query 'Contents[*].[Key,Size]' --output table

# Batch delete
aws s3api list-objects-v2 --bucket my-bucket --query 'Contents[*].Key' --output text | \
  xargs -I {} aws s3api delete-object --bucket my-bucket --key {}
```

## 5. Pagination and Filtering

### Handle Large Result Sets
```bash
# Auto-pagination
aws ec2 describe-instances --no-paginate  # Disable pagination

# Custom page size
aws ec2 describe-instances --max-items 10

# Filter results
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
               "Name=tag:Environment,Values=production"
```

## 6. Configuration Files

### ~/.aws/config
```ini
[default]
region = us-east-1
output = json

[profile production]
region = us-west-2
role_arn = arn:aws:iam::123456789012:role/prod-role
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/username

[profile development]
region = us-east-1
role_arn = arn:aws:iam::987654321098:role/dev-role
source_profile = default
```

### ~/.aws/credentials
```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[production]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

## 7. Common Commands

### EC2 Management
```bash
# Start instances
aws ec2 start-instances --instance-ids i-0123456789abcdef0

# Stop instances
aws ec2 stop-instances --instance-ids i-0123456789abcdef0

# Create security group
aws ec2 create-security-group --group-name my-sg --description "My security group"

# Authorize inbound rule
aws ec2 authorize-security-group-ingress --group-id sg-0123456 \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

### RDS Management
```bash
# Create database
aws rds create-db-instance --db-instance-identifier mydb --db-instance-class db.t3.micro \
  --engine postgres --master-username admin --master-user-password mypassword

# Create snapshot
aws rds create-db-snapshot --db-instance-identifier mydb --db-snapshot-identifier mydb-snapshot

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier mydb-restored \
  --db-snapshot-identifier mydb-snapshot
```

### Lambda Deployment
```bash
# Package function
zip function.zip lambda_function.py

# Create function
aws lambda create-function --function-name my-function --runtime python3.11 \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --handler lambda_function.lambda_handler --zip-file fileb://function.zip

# Update code
aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip

# Invoke function
aws lambda invoke --function-name my-function --payload '{"key":"value"}' response.json
```

## 8. Error Handling & Debugging

### Enable Debug Mode
```bash
# Enable debug output
aws ec2 describe-instances --debug 2>&1 | grep -E "^(DEBUG|Response)"

# Log to file
export AWS_DEBUG=true
aws ec2 describe-instances > /tmp/aws-debug.log 2>&1
```

### Common Error Codes
- **InvalidParameterValue**: Invalid input parameter
- **UnauthorizedOperation**: Missing credentials or permissions
- **InvalidInstanceID.NotFound**: Instance doesn't exist
- **AccessDenied**: Insufficient IAM permissions

### Retry Logic
```bash
# Use wait commands
aws ec2 wait instance-running --instance-ids i-0123456789abcdef0

# Poll with timeout
for i in {1..30}; do
  if aws ec2 describe-instances --instance-ids i-123 --query 'Reservations[0].Instances[0].State.Name' --output text | grep -q "running"; then
    echo "Instance is running"
    break
  fi
  sleep 10
done
```

## 9. Performance Optimization

### Parallel Operations
```bash
# Use xargs for parallel processing
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text | \
  xargs -P 5 -I {} aws ec2 describe-instances --instance-ids {}

# Use GNU parallel
aws s3api list-objects-v2 --bucket my-bucket --query 'Contents[*].Key' --output text | \
  parallel -j 4 'aws s3api head-object --bucket my-bucket --key {}'
```

### Caching
```bash
# Cache recent commands
history | grep "aws " | sort | uniq -c | sort -rn

# Create aliases
alias aws-instances='aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name]"'
```

## 10. Useful Tools & Extensions

### AWS CLI v2 Installation
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### AWS Shell
```bash
pip install aws-shell
aws-shell
```

### AWS SAM CLI
```bash
pip install aws-sam-cli
sam init  # Create new SAM project
sam build  # Build application
sam deploy --guided  # Deploy to AWS
```

## References
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [JMESPath Specification](https://jmespath.org/)
