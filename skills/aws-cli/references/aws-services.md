# AWS S3, Lambda & DynamoDB

## S3 Storage Classes

| Class | Cost | Access Time | Use Case |
|-------|------|-------------|----------|
| Standard | High | Immediate | Frequent access |
| IA | Medium | Minutes | Infrequent access |
| Glacier | Low  | Hours | Archival |

## Lambda Functions

```bash
# Create function
aws lambda create-function \
    --function-name my-function \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT:role/lambda-exec-role \
    --handler index.handler \
    --zip-file fileb://deployment.zip
```

## DynamoDB

Fast NoSQL database:

```bash
# Create table
aws dynamodb create-table \
    --table-name Users \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## VPC Basics

```
Internet Gateway
    ↓
Public Subnets (EC2, ALB)
    ↓
Private Subnets (Database, Cache)
    ↓
NAT Gateway (for internet access from private subnet)
```

## RDS (Managed Database)

vs Self-managed EC2 database:
- **RDS**: Automated backups, patching, high availability
- **EC2**: Full control, can run any database

Supported: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server
