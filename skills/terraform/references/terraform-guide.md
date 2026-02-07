# Terraform Guide

## Installation

```bash
# macOS
brew install terraform

# Verify
terraform version

# Autocompletion
terraform -install-autocomplete
```

## Project Structure

```
terraform/
├── main.tf              # Main configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── terraform.tfvars     # Variable values
├── backend.tf           # State backend
└── modules/
    └── vpc/            # Reusable module
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Basic Workflow

```bash
# Initialize working directory
terraform init

# Format code
terraform fmt

# Validate syntax
terraform validate

# See planned changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

## Main Configuration

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "MyWebServer"
  }
}
```

## Variables

```hcl
# variables.tf
variable "instance_count" {
  type        = number
  description = "Number of instances"
  default     = 1
}

variable "instance_type" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {
    Environment = "dev"
  }
}
```

## Outputs

```hcl
# outputs.tf
output "instance_ip" {
  value = aws_instance.web.public_ip
}

output "instance_id" {
  value       = aws_instance.web.id
  description = "EC2 instance ID"
}
```

## Using Variables

```bash
# Command line
terraform apply -var="instance_type=t2.small"

# From file
terraform apply -var-file="prod.tfvars"

# Env variable
export TF_VAR_instance_type=t2.large
```

## State Management

```bash
# Show state
terraform state list
terraform state show aws_instance.web

# Remove from state (but not destroy)
terraform state rm aws_instance.web

# Move/rename
terraform state mv aws_instance.old aws_instance.new

# Remote state
# In backend.tf:
terraform {
  backend "s3" {
    bucket = "my-tf-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
```

## Best Practices

1. **Use variables** - Reusability
2. **Remote state** - Share across team
3. **Plan first** - Review changes
4. **Version control** - Track changes
5. **Use modules** - DRY principle
