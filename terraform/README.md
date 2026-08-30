# Terraform AWS Infrastructure

Complete Infrastructure-as-Code for deploying the FastAPI MongoDB CRUD application to AWS using Terraform and Fargate.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Why These Choices](#why-these-choices)
3. [Prerequisites](#prerequisites)
4. [File Structure](#file-structure)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Networking](#networking)
8. [Scaling & Performance](#scaling--performance)
9. [Monitoring & Logging](#monitoring--logging)
10. [Cost Estimate](#cost-estimate)
11. [Troubleshooting](#troubleshooting)
12. [Cleanup](#cleanup)
13. [Security Best Practices](#security-best-practices)

## 🏗️ Architecture Overview

The infrastructure creates a **production-ready, highly available deployment** of your FastAPI application on AWS:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS Infrastructure                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Internet (0.0.0.0/0)                                              │
│    │                                                                │
│    ├─── HTTPS (443) / HTTP (80) ──────────────────────┐            │
│    │                                                   │            │
│    └──> ┌──────────────────────────────────────────┐  │            │
│         │ Application Load Balancer (Public)       │  │            │
│         │ - Routes traffic to ECS services         │  │            │
│         │ - Performs health checks                 │  │            │
│         │ - Handles SSL/TLS termination            │  │            │
│         └────────────────────────────────────────┬─┘  │            │
│                   Public Subnets                  │    │            │
│              (10.0.1.0/24, 10.0.2.0/24)          │    │            │
│    ────────────────────────────────────────────────────┤────────    │
│                                                   │    │            │
│         ┌─────────────────────────────────────────┤────┘            │
│         │                                          │                │
│    Private Subnets (10.0.10.0/24, 10.0.20.0/24)  │                │
│         │                                          │                │
│         ├──> ┌────────────────────────────────────┴──┐              │
│         │    │ ECS Fargate Tasks (2 min, 10 max)   │              │
│         │    │ - Port 8000 (FastAPI)               │              │
│         │    │ - Auto-scaling (CPU 70%, Mem 80%)  │              │
│         │    │ - CloudWatch logs                   │              │
│         │    └────────────┬──────────────────────┬─┘              │
│         │                 │                       │                │
│         │                 └──────────────────────┼────────┐       │
│         │                                         │        │       │
│         └──> ┌─────────────────────────────────┐  │        │       │
│              │ DocumentDB Cluster              │  │        │       │
│              │ - MongoDB-compatible            │  │        │       │
│              │ - Multi-AZ (Primary + Replica) │  │        │       │
│              │ - 7-day backups                │  │        │       │
│              │ - Port 27017                   │  │        │       │
│              └───────────────────────────────┘  │        │       │
│                                                 │        │       │
│    ┌────────────────────────────────────────────┤        │       │
│    │ CloudWatch (Monitoring & Logging)          │        │       │
│    │ - ECS logs (/ecs/books-api)                │        │       │
│    │ - DocumentDB logs (audit, error, etc)     │        │       │
│    │ - Alarms (CPU, connections, latency)     │        │       │
│    │ - Container Insights                      │        │       │
│    └───────────────────────────────────────────┘        │       │
│                                                         │       │
│    ┌────────────────────────────────────────────────────┤       │
│    │ AWS Secrets Manager                                │       │
│    │ - Stores MongoDB connection string                │       │
│    │ - Database username/password                      │       │
│    └────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

VPC CIDR: 10.0.0.0/16
```

### Key Components

| Component | Purpose | Configuration |
|-----------|---------|----------------|
| **VPC** | Isolated network environment | 10.0.0.0/16 |
| **Public Subnets** | ALB placement | 10.0.1.0/24 (AZ1), 10.0.2.0/24 (AZ2) |
| **Private Subnets** | ECS & DocumentDB | 10.0.10.0/24 (AZ1), 10.0.20.0/24 (AZ2) |
| **Internet Gateway** | Public internet access | Attached to VPC |
| **NAT Gateways** | Private subnet internet | 1 per AZ with Elastic IP |
| **ECS Fargate** | Containerized application | 256 CPU, 512 MB memory |
| **DocumentDB** | MongoDB-compatible database | db.t3.small, multi-AZ |
| **ALB** | Load balancing & routing | HTTP/80, HTTPS/443 (optional) |
| **CloudWatch** | Logging & monitoring | Logs, metrics, alarms |
| **Secrets Manager** | Credential management | MongoDB connection URL |

## 🎯 Why These Choices

### Container Hosting: ECS Fargate vs Alternatives

**Chosen: AWS ECS Fargate**

**Why?**
- **Serverless containers**: No EC2 instance management needed
- **Auto-scaling**: Automatically scales based on CPU (70%) and memory (80%)
- **Cost-effective**: Pay only for actual resource consumption (per second)
- **Integration**: Built-in CloudWatch logging, IAM roles, VPC networking
- **Maintenance**: AWS manages patching and availability

**Alternatives considered:**
- ❌ **EC2 + ECS**: More control but higher operational overhead, need to manage instances
- ❌ **Kubernetes (EKS)**: Overkill for single-service application, higher complexity
- ❌ **App Runner**: Limited customization, less flexibility with networking

### Database: DocumentDB vs Alternatives

**Chosen: AWS DocumentDB**

**Why?**
- **MongoDB-compatible**: Uses existing Motor driver without code changes
- **Managed service**: Automatic backups, patches, point-in-time recovery
- **Multi-AZ**: Automatic failover for high availability
- **Private VPC**: Database not exposed to internet
- **Cost**: Cheaper than self-managed MongoDB or Atlas for this scale
- **Integration**: IAM authentication, CloudWatch monitoring, Secrets Manager

**Alternatives considered:**
- ❌ **MongoDB Atlas**: Fully managed but external vendor, higher cost for enterprise
- ❌ **Self-managed MongoDB on EC2**: Full control but operational overhead
- ❌ **RDS (PostgreSQL)**: Would require schema migration from MongoDB

### Load Balancing: ALB vs Alternatives

**Chosen: Application Load Balancer**

**Why?**
- **Application-aware**: Routes based on HTTP paths, hostnames, headers
- **Health checks**: Automatic detection and removal of unhealthy instances
- **TLS termination**: Can offload SSL/HTTPS processing
- **Integration**: Direct integration with ECS service
- **Pricing**: Simple, predictable pricing model

**Alternatives considered:**
- ❌ **Network Load Balancer (NLB)**: Overkill for HTTP API, designed for millions of RPS
- ❌ **CloudFront**: More for CDN caching, adds latency for API calls
- ❌ **API Gateway**: Good for serverless but adds vendor lock-in

### Networking: VPC with Public/Private Subnets

**Why Multi-Tier Networking?**

- **Security**: Database and application isolated from direct internet access
- **Compliance**: Least-privilege access patterns
- **Flexibility**: Can add more resources (caches, workers) without internet exposure
- **NAT Gateways**: Allows private resources to reach internet for updates/external APIs

**Security Group Rules:**
```
ALB Security Group:
  Inbound: 0.0.0.0/0 → 80 (HTTP)
  Inbound: 0.0.0.0/0 → 443 (HTTPS, optional)
  
ECS Security Group:
  Inbound: ALB SG → 8000 (only from load balancer)
  
DocumentDB Security Group:
  Inbound: ECS SG → 27017 (only from ECS tasks)
```

## 📋 Prerequisites

Before deploying, ensure you have:

### Required Tools

- **Terraform 1.0+** - Infrastructure as Code
  ```bash
  brew install terraform  # macOS
  # or download from: https://www.terraform.io/downloads.html
  ```

- **AWS CLI v2** - AWS command-line interface
  ```bash
  brew install awscli  # macOS
  # or: https://aws.amazon.com/cli/
  ```

- **Docker** - For building and pushing the application image
  ```bash
  brew install docker  # macOS
  ```

### AWS Setup

1. **AWS Account** with appropriate permissions
2. **IAM User with Programmatic Access**
   - Permissions: EC2, ECS, RDS, VPC, CloudWatch, Secrets Manager, IAM
   - Access Key ID and Secret Access Key

3. **AWS Credentials Configured**
   ```bash
   aws configure
   # Enter: Access Key ID, Secret Access Key, Default region, Default output format
   
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

4. **ECR Repository** for Docker image
   ```bash
   # Create repository in ECR
   aws ecr create-repository --repository-name books-api --region us-east-1
   
   # Get login token and push image
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   docker build -t books-api .
   docker tag books-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/books-api:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/books-api:latest
   ```

### Application Prerequisites

- Docker image built and pushed to ECR
- Application environment variables defined
- Database migrations (if any) prepared

## 📁 File Structure

```
terraform/
├── README.md                      # This file
├── main.tf                        # Provider config, version constraints
├── variables.tf                   # Input variables with validation
├── vpc.tf                         # VPC, subnets, gateways, security groups
├── ecs.tf                         # ECS cluster, tasks, services, scaling
├── documentdb.tf                  # DocumentDB cluster, instances, monitoring
├── alb.tf                         # Application load balancer, target groups
├── outputs.tf                     # Output values (endpoints, DNS, IDs)
├── terraform.tfvars.example       # Example configuration (template)
└── terraform.tfvars               # Actual configuration (create from .example)
```

### File Descriptions

| File | Responsibility | Resources |
|------|---------------|-----------| 
| `main.tf` | Terraform version, AWS provider, defaults | 1 |
| `variables.tf` | Input parameters with validation rules | 12 variables |
| `vpc.tf` | VPC networking infrastructure | 19 resources |
| `ecs.tf` | ECS Fargate cluster & services | 14 resources |
| `documentdb.tf` | DocumentDB database cluster | 13 resources |
| `alb.tf` | Application load balancer | 6 resources |
| `outputs.tf` | Output values for deployment info | 20 outputs |

**Total: ~50+ AWS resources created**

## ⚙️ Configuration

### Step 1: Create Configuration File

```bash
# Copy example to actual config
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

### Step 2: Update Variables

Edit `terraform.tfvars` with your specific values:

```hcl
aws_region          = "us-east-1"           # AWS region
app_name            = "books-api"           # Application name (alphanumeric, hyphens)
environment         = "production"          # development, staging, production
ecr_image_uri       = "YOUR_ECR_URI:latest" # Full ECR image URI

# Database credentials (store securely!)
db_username         = "bookadmin"           # 1-16 characters
db_password         = "SecurePassword123!"  # 8+ chars, upper, lower, numbers

# ECS configuration
ecs_task_cpu        = 256                   # 256, 512, 1024, 2048, 4096
ecs_task_memory     = 512                   # Must be compatible with CPU
ecs_desired_count   = 2                     # Starting task count
ecs_min_capacity    = 2                     # Minimum tasks (HA)
ecs_max_capacity    = 10                    # Maximum tasks (cost control)

# Database
db_backup_retention = 7                     # Days (1-35)

# Tags (optional)
tags = {
  Team        = "platform"
  CostCenter  = "engineering"
  ManagedBy   = "Terraform"
}
```

### Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | us-east-1 | AWS region (e.g., us-east-1, eu-west-1) |
| `app_name` | string | books-api | App name for resource naming (32 chars max) |
| `environment` | string | production | Environment (development, staging, production) |
| `ecr_image_uri` | string | required | Full ECR image URI (account-id.dkr.ecr.region.amazonaws.com/repo:tag) |
| `db_username` | string | required | DocumentDB admin username (1-16 chars) |
| `db_password` | string | required | DocumentDB password (8+ chars, uppercase, lowercase, numbers) |
| `ecs_task_cpu` | number | 256 | Task CPU (256, 512, 1024, 2048, 4096) |
| `ecs_task_memory` | number | 512 | Task memory in MB (must be valid for CPU) |
| `ecs_desired_count` | number | 2 | Desired number of tasks (1-10) |
| `ecs_min_capacity` | number | 2 | Minimum tasks for auto-scaling (1-10) |
| `ecs_max_capacity` | number | 10 | Maximum tasks for auto-scaling (ecs_min_capacity to 10) |
| `db_backup_retention` | number | 7 | Backup retention days (1-35) |
| `tags` | map(string) | {} | Additional tags for all resources |

### Valid CPU/Memory Combinations

Not all CPU and memory combinations are valid. Valid combinations:

```
CPU 256:  512, 1024, 2048 MB
CPU 512:  1024, 2048, 3072, 4096 MB
CPU 1024: 2048, 3072, 4096, 5120, 6144, 7168, 8192 MB
CPU 2048: 4096, 5120, 6144, 7168, 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, 16384 MB
CPU 4096: 8192-30720 MB (1024 MB increments)
```

## 🚀 Deployment

### Step 1: Initialize Terraform

```bash
cd terraform

# Initialize Terraform (downloads providers, prepares backend)
terraform init
```

**Output:** Creates `.terraform/` directory with AWS provider

### Step 2: Validate Configuration

```bash
# Validate syntax and logic
terraform validate

# Check formatting
terraform fmt -check

# Or auto-format files
terraform fmt -recursive .
```

### Step 3: Plan Deployment

```bash
# Generate execution plan
terraform plan -out=tfplan

# This shows:
# - Resources to be created
# - Resource changes
# - Destroyed resources
```

**Review the plan carefully!** It will show:
- 1 VPC with subnets
- 2 NAT Gateways (charges!)
- 1 ALB
- 1 ECS cluster and service
- 2 DocumentDB instances
- ~10 CloudWatch resources
- IAM roles and policies

### Step 4: Apply Configuration

```bash
# Deploy infrastructure (requires user confirmation)
terraform apply tfplan

# Or plan and apply in one step:
terraform apply
```

**This will:**
1. Create all VPC resources (~5 minutes)
2. Create DocumentDB cluster (~15 minutes)
3. Create ECS cluster and service (~5 minutes)
4. Create ALB and target groups (~2 minutes)
5. Launch initial tasks (~1 minute)

**Total deployment time: ~30 minutes**

### Step 5: Verify Deployment

```bash
# Get all outputs
terraform output

# Get specific output
terraform output alb_dns_name

# Test health endpoint
curl http://<ALB_DNS_NAME>/health

# Access Swagger UI
open http://<ALB_DNS_NAME>/docs
```

## 🌐 Networking

### VPC Structure

```
VPC: 10.0.0.0/16
│
├── Public Subnets (Internet-facing)
│   ├── 10.0.1.0/24 (AZ: us-east-1a)
│   │   └── ALB Instance 1
│   └── 10.0.2.0/24 (AZ: us-east-1b)
│       └── ALB Instance 2
│
├── Private Subnets (No direct internet)
│   ├── 10.0.10.0/24 (AZ: us-east-1a)
│   │   ├── ECS Task 1
│   │   └── DocumentDB Primary
│   └── 10.0.20.0/24 (AZ: us-east-1b)
│       ├── ECS Task 2
│       └── DocumentDB Replica
│
├── Internet Gateway
│   └── Attached to VPC, provides internet access to public subnets
│
├── NAT Gateways
│   ├── NAT-AZ1: in public subnet, serves private-10.0.10.0/24
│   └── NAT-AZ2: in public subnet, serves private-10.0.20.0/24
│
└── Route Tables
    ├── Public: 0.0.0.0/0 → IGW
    └── Private: 0.0.0.0/0 → NAT Gateway
```

### Security Groups

#### ALB Security Group (Ingress)

```
Protocol | Port | Source      | Purpose
---------|------|-------------|-------------------
TCP      | 80   | 0.0.0.0/0   | HTTP (anyone)
TCP      | 443  | 0.0.0.0/0   | HTTPS (optional)
```

#### ECS Security Group (Ingress)

```
Protocol | Port | Source           | Purpose
---------|------|------------------|------------------------
TCP      | 8000 | ALB SG           | Application traffic from ALB only
```

#### DocumentDB Security Group (Ingress)

```
Protocol | Port | Source           | Purpose
---------|------|------------------|------------------------
TCP      | 27017| ECS SG           | MongoDB from ECS tasks only
```

### Connectivity Flow

```
User Request
    │
    ├─ HTTP (port 80)
    │
ALB (Public Subnet)
    │
    ├─ Connects to ECS Security Group
    │
ECS Tasks (Private Subnet)
    │
    ├─ Connects to DocumentDB Security Group
    │
DocumentDB (Private Subnet)
```

**Key Security Points:**
- ALB accessible from internet
- ECS only receives traffic from ALB
- DocumentDB only receives traffic from ECS
- Private subnets isolated from internet (except through NAT)

## 📈 Scaling & Performance

### Auto-Scaling Configuration

ECS service automatically scales based on metrics:

```
Metric          | Threshold | Action
----------------|-----------|-------------------------------------------
CPU Utilization | > 70%     | Scale UP (add tasks)
Memory Usage    | > 80%     | Scale UP (add tasks)
CPU Utilization | < 50%     | Scale DOWN (remove tasks)
Memory Usage    | < 60%     | Scale DOWN (remove tasks)
```

### Scaling Limits

```
Minimum tasks (high availability): 2
Maximum tasks (cost control):      10
```

### Task Configuration

```
CPU:    256 units (0.25 vCPU)
Memory: 512 MB
Price:  ~$0.04 per hour per task

With 2 tasks: ~$0.08/hour
With 10 tasks: ~$0.40/hour
Monthly: $57-288
```

### Scaling Example

```
Step 1: 2 tasks running
  └─ Average CPU: 40%

Step 2: Traffic spike, CPU reaches 75%
  └─ Alarm triggers, new task launched
  └─ Now: 3 tasks

Step 3: Traffic continues, CPU at 85%
  └─ Another task launched
  └─ Now: 4 tasks

Step 4: CPU distributed (60% per task)
  └─ No more scaling

Step 5: Traffic decreases, CPU at 35%
  └─ Scale down after 5 minutes
  └─ Back to 2 tasks (minimum)
```

### Scaling Time

- **Scale UP**: ~1-2 minutes (container download + startup)
- **Scale DOWN**: ~5-10 minutes (graceful shutdown)

### DocumentDB Scaling

DocumentDB uses **vertical scaling** (larger instance type), not horizontal:

```
Current: db.t3.small
Cost: ~$0.114/hour
Storage: Auto-scales up to 64 TB

To scale up:
  terraform apply -var="db_instance_class=db.t3.medium"
  # Takes 5-15 minutes for failover
```

## 📊 Monitoring & Logging

### CloudWatch Logs

Logs are automatically sent to CloudWatch Log Groups:

**ECS Logs:**
- Location: `/ecs/books-api`
- Retention: 7 days
- Includes: Application logs, errors, access logs

**DocumentDB Logs:**
- `/documentdb/books-api/audit`
- `/documentdb/books-api/error`
- `/documentdb/books-api/general`
- `/documentdb/books-api/slowquery`
- Retention: 7 days

### CloudWatch Metrics

Available metrics:

| Metric | Source | Threshold | Alert |
|--------|--------|-----------|-------|
| CPU Utilization | ECS Task | 70% | Scaling trigger |
| Memory Usage | ECS Task | 80% | Scaling trigger |
| UnhealthyHostCount | ALB | >= 1 | High priority |
| TargetResponseTime | ALB | > 2 sec | Medium priority |
| DatabaseConnections | DocumentDB | > 100 | Medium priority |
| CPUUtilization | DocumentDB | > 80% | Medium priority |

### Accessing Logs

```bash
# View ECS logs
aws logs tail /ecs/books-api --follow

# View DocumentDB error logs
aws logs tail /documentdb/books-api/error --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/books-api \
  --filter-pattern "ERROR"
```

### Setting Up Alerts

```bash
# Create SNS topic for notifications
aws sns create-topic --name books-api-alerts

# Subscribe to alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:books-api-alerts \
  --protocol email \
  --notification-endpoint your@email.com
```

Then update Terraform to add alarm actions:

```hcl
alarm_actions = [aws_sns_topic.alerts.arn]
```

## 💰 Cost Estimate

### Monthly Costs (Approximate)

```
ECS Fargate (2 tasks, 256 CPU, 512 MB)
  2 tasks × 730 hours × $0.04/hour = $58.40

DocumentDB (db.t3.small, multi-AZ)
  2 instances × 730 hours × $0.114/hour = $166.44
  Storage: $1 per GB/month (auto-scaling)

Application Load Balancer
  Fixed cost: $16.20
  LCU (capacity units): ~$5-10

NAT Gateway
  1 gateway: $32 (1 per AZ for HA)
  
Data Transfer
  In: Free
  Out: $0.02 per GB (typically <100 GB/month = $2)
  
CloudWatch (monitoring, logs)
  ~$2-5

─────────────────────────
TOTAL: ~$280-350/month
```

### Cost Optimization Tips

| Optimization | Monthly Savings | Tradeoff |
|--------------|-----------------|----------|
| 1 task instead of 2 | ~$30 | No high availability |
| db.t3.micro instead of small | ~$50 | Lower performance |
| Development environment | ~$150 | Not production-ready |
| 1 NAT Gateway instead of 2 | ~$32 | Single point of failure |
| 30-day backup instead of 7-day | ~$10 | Less recovery options |

## 🔧 Troubleshooting

### Terraform Issues

**Error: "Provider version constraints don't match"**
```bash
# Solution: Upgrade Terraform
terraform -version  # Check current
terraform init -upgrade  # Upgrade plugins
```

**Error: "Access Denied" from AWS**
```bash
# Solution: Check credentials
aws sts get-caller-identity
aws configure  # Re-enter credentials
```

**Error: "Validation errors in plan"**
```bash
# Solution: Check terraform.tfvars
terraform validate
# Look for: Invalid variable values, syntax errors
```

### Deployment Issues

**Application not starting**
```bash
# Check ECS task logs
aws logs tail /ecs/books-api --follow

# Check task status
aws ecs describe-tasks \
  --cluster books-api-cluster \
  --tasks TASK_ARN \
  --region us-east-1
```

**ALB showing unhealthy targets**
```bash
# Check health check response
curl -v http://ECS_TASK_IP:8000/health

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxxx \
  --region us-east-1
```

**Database connection failures**
```bash
# Check DocumentDB cluster status
aws rds describe-db-clusters \
  --db-cluster-identifier books-api-db \
  --region us-east-1

# Verify security group allows ECS to connect
# DocumentDB SG should have inbound from ECS SG on port 27017
```

### Performance Issues

**High latency**
```
Check: 
1. ALB target response time metric
2. ECS CPU/Memory utilization
3. DocumentDB CPU/Connections
4. Application logs for slow queries
```

**Out of memory errors**
```bash
# Current configuration in ECS task definition
# Increase ecs_task_memory in terraform.tfvars and reapply
```

**Database too slow**
```bash
# View slow query logs
aws logs filter-log-events \
  --log-group-name /documentdb/books-api/slowquery \
  --start-time $(date -d '1 hour ago' +%s)000

# Possible solutions:
# 1. Increase db instance class
# 2. Add indexes to frequently queried fields
# 3. Review query patterns
```

### Cost Issues

**Unexpected charges?**
```bash
# Check running resources
aws ec2 describe-instances
aws ecs describe-clusters
aws rds describe-db-clusters

# Identify unintended resources
# Delete unused resources:
terraform destroy -target aws_resource.name
```

## 🧹 Cleanup

### Destroy All Resources

```bash
cd terraform

# Review what will be destroyed
terraform plan -destroy

# Delete all infrastructure
terraform destroy

# Confirm when prompted
# This will take 15-20 minutes
```

### Manual Cleanup

Some resources may need manual cleanup:

```bash
# Delete EC2 key pairs (if created)
aws ec2 delete-key-pair --key-name books-api

# Delete CloudWatch log groups (retained by default)
aws logs delete-log-group --log-group-name /ecs/books-api

# Delete ECR images (not managed by Terraform)
aws ecr delete-repository \
  --repository-name books-api \
  --force \
  --region us-east-1
```

### Partial Destruction

To destroy specific resources:

```bash
# Destroy only ALB (keeps everything else)
terraform destroy -target aws_lb.alb

# Destroy ECS service but keep database
terraform destroy \
  -target aws_ecs_service.books_api \
  -target aws_ecs_task_definition.books_api
```

**⚠️ Warning:** Always use `terraform plan -destroy` before destroying anything!

## 🔒 Security Best Practices

### Network Security

✅ **Implemented:**
- Private subnets for application and database
- Security groups with least-privilege rules
- NAT Gateways for outbound internet access
- No direct internet access to database

🔒 **Recommended additions:**
- Enable VPC Flow Logs to monitor traffic
- Use VPC Endpoints for AWS services (S3, ECR)
- Implement bastion host for database access

### Application Security

✅ **Implemented:**
- Secrets Manager for database credentials
- IAM roles with minimal permissions
- Container image from private ECR

🔒 **Recommended:**
- Enable AWS WAF on ALB for protection
- Implement rate limiting
- Use HTTPS (requires certificate)

### Database Security

✅ **Implemented:**
- Database encryption at rest
- Database encryption in transit
- Private subnet (no internet access)
- Security group restricts access

🔒 **Recommended:**
- Enable IAM database authentication
- Enable audit logs
- Implement backup encryption

### Access Control

✅ **Implemented:**
- IAM roles with specific permissions
- Service-to-service communication via security groups

🔒 **Recommended:**
- MFA for AWS console access
- Rotate database credentials quarterly
- Audit IAM policies regularly

### Monitoring

✅ **Implemented:**
- CloudWatch logs for all services
- CloudWatch alarms for key metrics
- Container Insights for ECS monitoring

🔒 **Recommended:**
- Enable CloudTrail for API audit logging
- Send logs to centralized SIEM
- Set up log retention policies

## 📚 Additional Resources

### Official Documentation
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)
- [AWS DocumentDB](https://docs.aws.amazon.com/documentdb/)
- [AWS Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/)

### Terraform References
- [Terraform State Management](https://www.terraform.io/language/state)
- [Terraform Modules](https://www.terraform.io/language/modules)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices)

### AWS Best Practices
- [Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [AWS Cost Optimization](https://aws.amazon.com/architecture/cost-optimization/)

## ❓ FAQ

**Q: Can I use a single NAT Gateway?**
A: No - high availability requires one NAT Gateway per AZ. One would be a single point of failure.

**Q: Can I use a different database than DocumentDB?**
A: Yes - update `documentdb.tf` or replace with RDS, but requires migration.

**Q: How do I update the application without downtime?**
A: Push new image to ECR, then `terraform apply`. Blue/green deployments happen automatically.

**Q: Can I use my own domain name?**
A: Yes - use Route53 to alias your domain to the ALB DNS name.

**Q: How do I monitor costs?**
A: Use AWS Budgets and Cost Explorer. Check CloudWatch for resource utilization.

**Q: Is this suitable for production?**
A: Yes - multi-AZ, auto-scaling, encryption, monitoring are all included. Add WAF and HTTPS for hardening.

---

**Last Updated:** 2024
**Terraform Version:** 1.0+
**AWS Provider Version:** ~> 5.0
