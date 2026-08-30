# FastAPI MongoDB CRUD - AWS Infrastructure
# Terraform configuration for deploying the application to AWS using ECS Fargate,
# DocumentDB (MongoDB-compatible), and Application Load Balancer

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use remote state (S3 + DynamoDB)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "books-api/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.app_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  }
}

# Local variables for convenience
locals {
  container_name = "${var.app_name}-container"
  container_port = 8000
  app_log_group  = "/ecs/${var.app_name}"
}
