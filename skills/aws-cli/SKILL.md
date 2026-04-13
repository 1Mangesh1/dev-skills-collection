---
name: aws-cli
description: AWS CLI v2 mastery for S3, EC2, Lambda, IAM, CloudFormation, ECS, RDS, CloudWatch, SQS, SNS, Route 53, Secrets Manager, Parameter Store, and cost management. Use when user asks to "upload to S3", "launch EC2", "deploy Lambda", "configure AWS", "AWS profiles", "check AWS resources", "deploy stack", "create alarm", "manage secrets", "AWS costs", "presigned URL", "assume role", "SSO login", or any AWS command-line task.
---

# AWS CLI

Complete reference for AWS CLI v2 commands and patterns.

## Installation and Configuration

```bash
# macOS: brew install awscli
# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Setup (stores in ~/.aws/credentials and ~/.aws/config)
aws configure                       # default profile
aws configure --profile staging     # named profile
export AWS_PROFILE=staging          # set default for session
aws sts get-caller-identity         # check identity

# SSO
aws configure sso                   # interactive setup
aws sso login --profile my-sso-profile
```

```ini
# ~/.aws/config
[profile dev]
region = us-east-1
output = json

[profile prod]
role_arn = arn:aws:iam::123456789012:role/AdminRole
source_profile = dev

[profile prod-mfa]
role_arn = arn:aws:iam::123456789012:role/AdminRole
source_profile = dev
mfa_serial = arn:aws:iam::123456789012:mfa/my-user

[profile sso-profile]
sso_start_url = https://my-org.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = PowerUserAccess
```

## S3

```bash
# List
aws s3 ls
aws s3 ls s3://my-bucket/prefix/ --recursive --human-readable --summarize
# Copy
aws s3 cp file.txt s3://my-bucket/
aws s3 cp s3://my-bucket/file.txt ./
aws s3 cp largefile.zip s3://bucket/ --storage-class GLACIER
# Sync
aws s3 sync ./dist s3://my-bucket/
aws s3 sync ./dist s3://my-bucket/ --delete          # Mirror
aws s3 sync . s3://bucket/ --exclude "*.log" --include "*.txt"
# Remove
aws s3 rm s3://my-bucket/file.txt
aws s3 rm s3://my-bucket/ --recursive
# Presigned URL (temporary access)
aws s3 presign s3://my-bucket/file.txt --expires-in 3600
# Bucket create/delete
aws s3 mb s3://new-bucket --region us-west-2
aws s3 rb s3://non-empty-bucket --force
# Bucket policy, versioning, lifecycle (s3api)
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json
aws s3api put-bucket-versioning --bucket my-bucket \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket --lifecycle-configuration file://lifecycle.json
aws s3api put-public-access-block --bucket my-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

## EC2

```bash
# List instances
aws ec2 describe-instances --filters "Name=tag:Name,Values=web-*"
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,InstanceType,PublicIpAddress]' \
  --output table
# Launch instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 --instance-type t3.micro \
  --key-name my-key --security-group-ids sg-12345678 \
  --subnet-id subnet-abcdef01 --count 1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-server}]'
# Start/stop/terminate
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
# Key pairs
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
chmod 400 my-key.pem
# Security groups
aws ec2 create-security-group --group-name my-sg --description "My SG" --vpc-id vpc-123
aws ec2 authorize-security-group-ingress \
  --group-id sg-123 --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 revoke-security-group-ingress \
  --group-id sg-123 --protocol tcp --port 22 --cidr 0.0.0.0/0
# AMI
aws ec2 create-image --instance-id i-123 --name "my-backup" --no-reboot
aws ec2 describe-images --owners self
```

## Lambda

```bash
# Create function
aws lambda create-function \
  --function-name my-func --runtime nodejs20.x \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --handler index.handler --zip-file fileb://function.zip
# Update code
zip -r function.zip . && aws lambda update-function-code \
  --function-name my-func --zip-file fileb://function.zip
# Invoke
aws lambda invoke --function-name my-func \
  --payload '{"key":"value"}' --cli-binary-format raw-in-base64-out output.json
# Function URL (public HTTPS endpoint)
aws lambda create-function-url-config --function-name my-func --auth-type NONE
# Layers
aws lambda publish-layer-version --layer-name my-layer \
  --zip-file fileb://layer.zip --compatible-runtimes nodejs20.x
aws lambda update-function-configuration --function-name my-func \
  --layers arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
# Environment variables
aws lambda update-function-configuration --function-name my-func \
  --environment "Variables={KEY=value,DB_HOST=localhost}"
# View logs
aws logs tail /aws/lambda/my-func --follow --since 1h
```

## IAM

```bash
# Users and access keys
aws iam list-users
aws iam create-user --user-name deploy-bot
aws iam create-access-key --user-name deploy-bot

# Policies
aws iam attach-user-policy --user-name deploy-bot \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam create-policy --policy-name my-policy --policy-document file://policy.json

# Roles
aws iam create-role --role-name my-role \
  --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name my-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Assume role (temporary credentials)
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/my-role \
  --role-session-name my-session
# Export returned AccessKeyId, SecretAccessKey, SessionToken

# Get session token with MFA
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/my-user --token-code 123456
```

## CloudFormation

```bash
# Deploy stack
aws cloudformation deploy \
  --template-file template.yaml --stack-name my-stack \
  --parameter-overrides Env=prod DbSize=large \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

# Describe stack and events
aws cloudformation describe-stacks --stack-name my-stack
aws cloudformation describe-stack-events --stack-name my-stack \
  --query 'StackEvents[].[Timestamp,LogicalResourceId,ResourceStatus]' --output table

# Stack outputs
aws cloudformation describe-stacks --stack-name my-stack \
  --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output table

# Delete and validate
aws cloudformation delete-stack --stack-name my-stack
aws cloudformation validate-template --template-body file://template.yaml
```

## ECS / Fargate

```bash
# List and describe
aws ecs list-clusters
aws ecs list-services --cluster my-cluster
aws ecs describe-services --cluster my-cluster --services my-service

# Deploy and scale
aws ecs update-service --cluster my-cluster --service my-service --force-new-deployment
aws ecs update-service --cluster my-cluster --service my-service --desired-count 3

# Tasks
aws ecs list-tasks --cluster my-cluster --service my-service
aws ecs describe-tasks --cluster my-cluster --tasks <task-arn>

# Exec into container
aws ecs execute-command --cluster my-cluster --task <task-id> \
  --container my-app --interactive --command "/bin/sh"

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-def.json
```

## RDS

```bash
# List instances
aws rds describe-db-instances \
  --query 'DBInstances[].[DBInstanceIdentifier,Engine,DBInstanceStatus]' --output table

# Create instance
aws rds create-db-instance \
  --db-instance-identifier my-db --db-instance-class db.t3.micro \
  --engine postgres --engine-version 16.1 \
  --master-username admin --master-user-password 'SecurePass123!' \
  --allocated-storage 20

# Snapshot and restore
aws rds create-db-snapshot \
  --db-instance-identifier my-db --db-snapshot-identifier my-db-snap
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier my-db-restored --db-snapshot-identifier my-db-snap

# Delete
aws rds delete-db-instance --db-instance-identifier my-db --skip-final-snapshot
```

## CloudWatch

```bash
# Tail and filter logs
aws logs describe-log-groups
aws logs tail /ecs/my-service --follow --since 30m
aws logs filter-log-events \
  --log-group-name /ecs/my-service --filter-pattern "ERROR"

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu --metric-name CPUUtilization --namespace AWS/EC2 \
  --statistic Average --period 300 --threshold 80 \
  --comparison-operator GreaterThanThreshold --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts \
  --dimensions Name=InstanceId,Value=i-123

# List alarms in ALARM state
aws cloudwatch describe-alarms --state-value ALARM

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 --metric-name CPUUtilization \
  --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z \
  --period 3600 --statistics Average --dimensions Name=InstanceId,Value=i-123
```

## SQS and SNS

```bash
# SQS
aws sqs create-queue --queue-name my-queue
aws sqs send-message --queue-url <url> --message-body '{"order_id": 42}'
aws sqs receive-message --queue-url <url> --max-number-of-messages 10 --wait-time-seconds 20
aws sqs delete-message --queue-url <url> --receipt-handle <handle>
aws sqs get-queue-attributes --queue-url <url> --attribute-names ApproximateNumberOfMessages

# SNS
aws sns create-topic --name my-topic
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:123:my-topic \
  --protocol email --notification-endpoint user@example.com
aws sns publish --topic-arn arn:aws:sns:us-east-1:123:my-topic --message "Deploy complete"
```

## Route 53

```bash
aws route53 list-hosted-zones
aws route53 list-resource-record-sets --hosted-zone-id Z1234567890

# Create/update record
aws route53 change-resource-record-sets --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [{"Action":"UPSERT","ResourceRecordSet":{
      "Name":"app.example.com","Type":"A","TTL":300,
      "ResourceRecords":[{"Value":"1.2.3.4"}]}}]}'
```

## Secrets Manager and Parameter Store

```bash
# Secrets Manager
aws secretsmanager create-secret --name my-app/db-pass --secret-string 'S3cret!'
aws secretsmanager get-secret-value --secret-id my-app/db-pass --query SecretString --output text
aws secretsmanager update-secret --secret-id my-app/db-pass --secret-string 'NewPass!'
aws secretsmanager delete-secret --secret-id my-app/db-pass --recovery-window-in-days 7

# Parameter Store
aws ssm put-parameter --name /app/config/db-host --value "db.example.com" --type String
aws ssm put-parameter --name /app/config/api-key --value "secret" --type SecureString
aws ssm get-parameter --name /app/config/api-key --with-decryption --query Parameter.Value --output text
aws ssm get-parameters-by-path --path /app/config/ --recursive --with-decryption
```

## Cost Explorer

```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

## Output Formatting and JMESPath

```bash
# Output formats
--output json | table | text | yaml

# JMESPath queries
--query 'Reservations[].Instances[].[InstanceId,State.Name]'          # Select fields
--query 'Reservations[].Instances[?State.Name==`running`].InstanceId' # Filter
--query 'length(Reservations[].Instances[])'                          # Count
--query 'sort_by(Buckets, &CreationDate)[].Name'                      # Sort
```

## Pagination and Debugging

```bash
# Disable auto-pagination (useful when piping)
aws s3api list-objects-v2 --bucket my-bucket --no-paginate

# Manual pagination
aws s3api list-objects-v2 --bucket my-bucket --max-items 100
aws s3api list-objects-v2 --bucket my-bucket --max-items 100 --starting-token <token>

# Debug API calls
aws s3 ls --debug
```

## Common Patterns

```bash
# Wait commands (block until resource reaches state)
aws ec2 wait instance-running --instance-ids i-123
aws rds wait db-instance-available --db-instance-identifier my-db
aws ecs wait services-stable --cluster my-cluster --services my-service
aws cloudformation wait stack-create-complete --stack-name my-stack

# Filter by tags
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" "Name=instance-state-name,Values=running"

# Dry run (test permissions without executing)
aws ec2 run-instances --dry-run --image-id ami-123 --instance-type t3.micro

# Region override
aws ec2 describe-instances --region eu-west-1

# Get account ID
aws sts get-caller-identity --query Account --output text
```
