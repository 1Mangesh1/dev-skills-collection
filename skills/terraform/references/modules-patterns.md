# Terraform Modules & Advanced Patterns

## Module Structure

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
  
  tags = {
    Name = var.vpc_name
  }
}

# modules/vpc/variables.tf
variable "vpc_name" {
  type = string
}

variable "cidr_block" {
  type = string
}

# modules/vpc/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}
```

## Using Modules

```hcl
# main.tf
module "vpc" {
  source = "./modules/vpc"
  
  vpc_name   = "production"
  cidr_block = "10.0.0.0/16"
}

module "vpc_dev" {
  source = "./modules/vpc"
  
  vpc_name   = "development"
  cidr_block = "10.1.0.0/16"
}
```

## For Each Loop

```hcl
variable "instance_names" {
  type = list(string)
  default = ["web-1", "web-2", "web-3"]
}

resource "aws_instance" "servers" {
  for_each = toset(var.instance_names)
  
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = each.value
  }
}

# Reference
output "instance_ips" {
  value = {
    for name, instance in aws_instance.servers :
    name => instance.public_ip
  }
}
```

## Conditionals

```hcl
variable "create_monitoring" {
  type = bool
  default = true
}

resource "aws_cloudwatch_alarm" "cpu" {
  count = var.create_monitoring ? 1 : 0
  
  alarm_name          = "high-cpu"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 80
}
```

## Data Sources

```hcl
# Get existing AWS VPC
data "aws_vpc" "default" {
  default = true
}

# Use in resource
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  subnet_id     = data.aws_vpc.default.main_route_table_id
}
```

## Local Values

```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = "MyApp"
    Managed     = "Terraform"
  }
}

resource "aws_instance" "web" {
  tags = merge(
    local.common_tags,
    {
      Name = "WebServer"
    }
  )
}
```
