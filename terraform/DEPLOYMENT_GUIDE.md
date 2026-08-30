# Terraform AWS Deployment Guide

Quick reference for deploying the FastAPI application to AWS using Terraform.

## ⏱️ Quick Start (10 Minutes)

### 1. Prepare Docker Image (5 min)

```bash
# Navigate to project root
cd /path/to/project

# Build Docker image
docker build -t books-api .

# Create ECR repository (if not exists)
aws ecr create-repository --repository-name books-api --region us-east-1

# Get ECR URI
ECR_URI=$(aws ecr describe-repositories \
  --repository-names books-api \
  --region us-east-1 \
  --query 'repositories[0].repositoryUri' \
  --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URI

# Tag and push image
docker tag books-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Save ECR URI for Terraform
echo "ECR_URI=$ECR_URI"
```

### 2. Configure Terraform (3 min)

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration (replace YOUR_ECR_URI with actual URI from step 1)
nano terraform.tfvars
```

Edit these critical values in `terraform.tfvars`:
```hcl
ecr_image_uri   = "YOUR_ECR_URI:latest"  # From step 1
db_password     = "SecurePassword123!"   # Change to strong password
db_username     = "bookadmin"            # Change if desired
```

### 3. Deploy (2 min)

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Review the plan output, then apply
terraform apply tfplan

# This takes 25-30 minutes to complete
```

### 4. Get API URL (1 min)

```bash
# Once deployment completes
terraform output alb_dns_name

# Test API
curl http://$(terraform output -raw alb_dns_name)/health

# Access Swagger UI
open http://$(terraform output -raw alb_dns_name)/docs
```

## 📋 Detailed Deployment Steps

### Prerequisites Check

```bash
# Verify all required tools
terraform -version      # Should be 1.0+
aws --version          # Should be 2.0+
docker --version       # Should be 20.0+

# Verify AWS credentials
aws sts get-caller-identity

# Verify AWS region
aws configure get region  # Should show us-east-1 (or your region)
```

### Step 1: Create Docker Image

```bash
# From project root
docker build -t books-api:latest .

# Verify image
docker run -it --rm \
  -e MONGODB_URL="mongodb://localhost:27017" \
  -e DATABASE_NAME="test_db" \
  -p 8000:8000 \
  books-api:latest

# Test in new terminal
curl http://localhost:8000/health
```

### Step 2: Push to ECR

```bash
# Create repository if needed
aws ecr create-repository \
  --repository-name books-api \
  --region us-east-1

# Get repository URI
REPO_URI=$(aws ecr describe-repositories \
  --repository-names books-api \
  --region us-east-1 \
  --query 'repositories[0].repositoryUri' \
  --output text)

echo "Repository URI: $REPO_URI"

# Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $REPO_URI

# Tag image
docker tag books-api:latest $REPO_URI:latest
docker tag books-api:latest $REPO_URI:$(date +%s)

# Push image
docker push $REPO_URI:latest
docker push $REPO_URI:$(date +%s)

# Verify push
aws ecr describe-images \
  --repository-name books-api \
  --region us-east-1
```

### Step 3: Configure Terraform

```bash
# Copy template
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Required edits
cat > terraform/terraform.tfvars << EOF
aws_region     = "us-east-1"
app_name       = "books-api"
environment    = "production"
ecr_image_uri  = "$REPO_URI:latest"  # From step 2

db_username    = "bookadmin"
db_password    = "MySecurePassword123!"  # Change this!

ecs_task_cpu       = 256
ecs_task_memory    = 512
ecs_desired_count  = 2
ecs_min_capacity   = 2
ecs_max_capacity   = 10

db_backup_retention = 7

tags = {
  Environment = "production"
  ManagedBy   = "Terraform"
}
EOF
```

### Step 4: Initialize Terraform

```bash
cd terraform

# Initialize (downloads AWS provider)
terraform init

# Output:
# - Terraform has been successfully configured!
# - You can now begin working with Terraform.
```

### Step 5: Validate Configuration

```bash
# Check syntax
terraform validate

# Output:
# Success! The configuration is valid.

# Check formatting
terraform fmt -check
terraform fmt -recursive .
```

### Step 6: Plan Deployment

```bash
# Generate plan
terraform plan -out=tfplan

# This will:
# 1. Query AWS for existing resources
# 2. Calculate differences
# 3. Show all resources to create/modify/destroy
# 4. Save plan to tfplan file

# Key lines to check:
# "Plan: XX to add, 0 to change, 0 to destroy"
```

**Plan output example:**
```
Terraform will perform the following actions:

  # aws_vpc.main will be created
  + resource "aws_vpc" "main" {
      + cidr_block           = "10.0.0.0/16"
      + enable_dns_hostnames = true
      + ...
    }

  # aws_subnet.public[0] will be created
  + resource "aws_subnet" "public" { ... }

...

Plan: 51 to add, 0 to change, 0 to destroy.
```

### Step 7: Review Security

Before applying, verify security configuration:

```bash
# Review security groups
grep -A 5 "ingress {" *.tf

# Review IAM roles
grep -A 5 "policy = " *.tf

# Verify no public database access
grep "publicly_accessible" documentdb.tf
# Should be: publicly_accessible = false
```

### Step 8: Apply Configuration

```bash
# Deploy infrastructure
terraform apply tfplan

# This will:
# 1. Create VPC and networking (5 min)
# 2. Create DocumentDB cluster (15 min)
# 3. Create ECS cluster and service (5 min)
# 4. Create ALB (2 min)
# 5. Launch application tasks (1 min)

# Total time: 25-30 minutes

# Watch progress
watch -n 5 'aws ecs describe-services \
  --cluster books-api-cluster \
  --services books-api-service \
  --region us-east-1 \
  --query "services[0].desiredCount" \
  --output text'
```

### Step 9: Verify Deployment

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "API URL: http://$ALB_DNS"

# Test health endpoint
curl http://$ALB_DNS/health
# Expected response:
# {"status":"healthy","environment":"production","database":"connected"}

# Check Swagger UI
open http://$ALB_DNS/docs

# Check ReDoc
open http://$ALB_DNS/redoc

# Test actual endpoints
curl -X GET http://$ALB_DNS/api/v1/books

# Get all outputs
terraform output
```

### Step 10: Get Database Connection Info

```bash
# Retrieve MongoDB connection details
MONGODB_SECRET=$(terraform output -raw mongodb_secret_arn)

# Get secret value from AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id $MONGODB_SECRET \
  --region us-east-1 \
  --query SecretString \
  --output text

# Output includes: username, password, host, port, dbname
```

## 🔄 Common Operations

### Update Application Code

```bash
# 1. Build new image
docker build -t books-api:latest .

# 2. Push to ECR
docker push $ECR_URI:latest

# 3. Update ECS service (auto-deploys)
terraform apply

# 4. Monitor deployment
aws ecs describe-services \
  --cluster books-api-cluster \
  --services books-api-service \
  --region us-east-1
```

### Scale Application

```bash
# Edit terraform.tfvars
# Change ecs_desired_count, ecs_min_capacity, or ecs_max_capacity

# Apply changes
terraform apply

# Example: scale to 5 tasks
sed -i 's/ecs_desired_count   = .*/ecs_desired_count   = 5/' terraform.tfvars
terraform apply
```

### Monitor Logs

```bash
# ECS application logs
aws logs tail /ecs/books-api --follow

# DatabaseDB error logs
aws logs tail /documentdb/books-api/error --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/books-api \
  --filter-pattern "ERROR"
```

### Check Resource Status

```bash
# ECS service status
aws ecs describe-services \
  --cluster books-api-cluster \
  --services books-api-service

# DocumentDB cluster status
aws rds describe-db-clusters \
  --db-cluster-identifier books-api-db

# ALB status
aws elbv2 describe-load-balancers \
  --names books-api-alb

# Target health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw alb_target_group_arn)
```

### Create Database Backup

```bash
# Create manual snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier books-api-db \
  --db-cluster-snapshot-identifier books-api-backup-$(date +%s)

# List snapshots
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier books-api-db
```

## ⚠️ Troubleshooting

### Application Won't Start

```bash
# Check task logs
aws logs tail /ecs/books-api --follow

# Check task status
aws ecs describe-tasks \
  --cluster books-api-cluster \
  --tasks $(aws ecs list-tasks \
    --cluster books-api-cluster \
    --query 'taskArns[0]' \
    --output text) \
  --region us-east-1

# Check if image exists in ECR
aws ecr describe-images \
  --repository-name books-api
```

### Database Connection Failed

```bash
# Verify DocumentDB is running
aws rds describe-db-clusters \
  --db-cluster-identifier books-api-db

# Check security group
aws ec2 describe-security-groups \
  --filter Name=group-name,Values=books-api-documentdb-sg

# Verify secret in Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id books-api-mongodb-secret
```

### ALB Shows Unhealthy Targets

```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw alb_target_group_arn)

# Test health endpoint directly
ECS_IP=$(aws ecs describe-tasks \
  --cluster books-api-cluster \
  --tasks $(aws ecs list-tasks \
    --cluster books-api-cluster \
    --query 'taskArns[0]' \
    --output text) \
  --query 'tasks[0].containerInstanceArn' \
  --output text)

curl -v http://$ECS_IP:8000/health
```

### High Costs

```bash
# Check running resources
aws ec2 describe-instances --query 'Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name}'

aws rds describe-db-instances

aws elbv2 describe-load-balancers

# Delete unused resources if needed
terraform destroy -target aws_lb.alb
```

## 🚀 Performance Optimization

### Reduce Deployment Time

```bash
# Skip DocumentDB backup during testing
terraform apply -var="db_backup_retention=1"

# Use spot instances
terraform apply -var="use_fargate_spot=true"
```

### Optimize Costs

```bash
# Reduce task count in off-hours
terraform apply -var="ecs_desired_count=1"

# Use smaller instance types
terraform apply \
  -var="ecs_task_cpu=128" \
  -var="ecs_task_memory=256"

# Reduce database retention
terraform apply -var="db_backup_retention=1"
```

## 📊 Monitoring Setup

### Set Up Email Alerts

```bash
# Create SNS topic
SNS_TOPIC=$(aws sns create-topic \
  --name books-api-alerts \
  --region us-east-1 \
  --query 'TopicArn' \
  --output text)

# Subscribe email
aws sns subscribe \
  --topic-arn $SNS_TOPIC \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription (check email)

# Add to terraform.tfvars:
# alarm_actions = ["$SNS_TOPIC"]
```

### Create Custom Dashboard

```bash
# CloudWatch dashboard with key metrics
aws cloudwatch put-dashboard \
  --dashboard-name books-api \
  --dashboard-body file://dashboard.json
```

## 🧹 Cleanup

### Full Cleanup

```bash
# Backup data first!
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier books-api-db \
  --db-cluster-snapshot-identifier final-backup

# Destroy infrastructure
terraform destroy

# Confirm deletion
```

### Partial Cleanup

```bash
# Delete only ECS service (keep database)
terraform destroy -target aws_ecs_service.books_api

# Delete only ALB
terraform destroy -target aws_lb.alb
```

## ✅ Deployment Checklist

- [ ] Docker image built and tested locally
- [ ] ECR repository created
- [ ] Image pushed to ECR
- [ ] AWS credentials configured
- [ ] terraform.tfvars updated with ECR URI and database password
- [ ] `terraform init` completed
- [ ] `terraform validate` passed
- [ ] `terraform plan` reviewed (51 resources)
- [ ] Security groups verified (least-privilege)
- [ ] `terraform apply` completed (25-30 min)
- [ ] Health endpoint returns "healthy"
- [ ] Swagger UI accessible
- [ ] Sample API request successful
- [ ] CloudWatch logs configured
- [ ] Monitoring alarms set up (optional)
- [ ] Database backup scheduled
- [ ] Team notified of new API endpoint

## 📞 Support

For issues:
1. Check CloudWatch logs: `aws logs tail /ecs/books-api --follow`
2. Review Terraform state: `terraform state list`
3. Check AWS console for resource status
4. Run `terraform plan` to see what changed
5. Review this guide's troubleshooting section

---

**Deployment Time:** 25-30 minutes
**Cost:** ~$280-350/month
**Uptime:** 99.9% (multi-AZ)
