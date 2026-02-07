# AWS EC2 Essentials

## Instance Types

| Type | Use Case | vCPU | Memory | Cost |
|------|----------|------|--------|------|
| t3.micro | Dev, Testing | 1 | 1GB | $0.0104/hr |
| t3.small | Light workload | 2 | 2GB | $0.0208/hr |
| t3.medium | Apps | 2 | 4GB | $0.0416/hr |
| m5.large | General | 2 | 8GB | $0.096/hr |
| c5.large | Compute | 2 | 4GB | $0.085/hr |

## Common Operations

### Create Instance
```bash
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t3.micro
```

### Start/Stop
```bash
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

### Terminate
```bash
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

## Security Groups

```bash
# Create security group
aws ec2 create-security-group --group-name my-sg --description "My security group"

# Add ingress rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

# Add SSH rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp --port 22 --cidr YOUR_IP/32
```

## Cost Optimization

1. **Use right-sized instances** - Don't over-provision
2. **Reserved instances** - 30-40% discount for 1/3-year
3. **Spot instances** - 70% discount for flexible workloads
4. **Auto-scaling** - Scale down when not needed
5. **Delete unused resources** - EBS volumes, elastic IPs, snapshots
