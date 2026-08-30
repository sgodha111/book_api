# Input variables for the Terraform configuration

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-\\d{1}$", var.aws_region))
    error_message = "AWS region must be valid (e.g., us-east-1, eu-west-1)."
  }
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "books-api"

  validation {
    condition     = length(var.app_name) <= 32 && can(regex("^[a-z0-9-]*$", var.app_name))
    error_message = "App name must be lowercase alphanumeric with hyphens, max 32 characters."
  }
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "ecr_image_uri" {
  description = "ECR image URI for the FastAPI application"
  type        = string

  validation {
    condition     = can(regex("^\\d+\\.dkr\\.ecr\\.[a-z0-9-]+\\.amazonaws\\.com/.+:.+$", var.ecr_image_uri))
    error_message = "ECR image URI must be in format: ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPO:TAG"
  }
}

variable "db_username" {
  description = "DocumentDB master username"
  type        = string
  default     = "admin"

  validation {
    condition     = length(var.db_username) >= 1 && length(var.db_username) <= 16
    error_message = "DB username must be between 1 and 16 characters."
  }
}

variable "db_password" {
  description = "DocumentDB master password (must change from default)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8 && can(regex("[A-Z]", var.db_password)) && can(regex("[a-z]", var.db_password)) && can(regex("[0-9]", var.db_password))
    error_message = "DB password must be at least 8 characters with uppercase, lowercase, and numbers."
  }
}

variable "ecs_task_cpu" {
  description = "ECS task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256

  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.ecs_task_cpu)
    error_message = "CPU must be one of: 256, 512, 1024, 2048, 4096."
  }
}

variable "ecs_task_memory" {
  description = "ECS task memory in MB"
  type        = number
  default     = 512

  validation {
    condition     = contains([512, 1024, 2048, 3072, 4096, 5120, 6144, 7168, 8192], var.ecs_task_memory)
    error_message = "Memory must be valid ECS Fargate option."
  }
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 2

  validation {
    condition     = var.ecs_desired_count >= 1 && var.ecs_desired_count <= 10
    error_message = "Desired count must be between 1 and 10."
  }
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks for auto-scaling"
  type        = number
  default     = 2

  validation {
    condition     = var.ecs_min_capacity >= 1
    error_message = "Min capacity must be at least 1."
  }
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks for auto-scaling"
  type        = number
  default     = 10

  validation {
    condition     = var.ecs_max_capacity >= var.ecs_min_capacity
    error_message = "Max capacity must be >= min capacity."
  }
}

variable "db_backup_retention" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention >= 1 && var.db_backup_retention <= 35
    error_message = "Backup retention must be between 1 and 35 days."
  }
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
