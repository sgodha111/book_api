# Output values for Terraform configuration

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name

  depends_on = [aws_lb.main]
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn

  depends_on = [aws_lb.main]
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id

  depends_on = [aws_lb.main]
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name

  depends_on = [aws_ecs_cluster.main]
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn

  depends_on = [aws_ecs_cluster.main]
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name

  depends_on = [aws_ecs_service.app]
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.app.arn

  depends_on = [aws_ecs_task_definition.app]
}

output "documentdb_cluster_endpoint" {
  description = "DocumentDB cluster endpoint"
  value       = aws_docdb_cluster.main.endpoint

  depends_on = [aws_docdb_cluster.main]
}

output "documentdb_reader_endpoint" {
  description = "DocumentDB cluster reader endpoint"
  value       = aws_docdb_cluster.main.reader_endpoint

  depends_on = [aws_docdb_cluster.main]
}

output "documentdb_cluster_resource_id" {
  description = "DocumentDB cluster resource ID"
  value       = aws_docdb_cluster.main.cluster_resource_id

  depends_on = [aws_docdb_cluster.main]
}

output "mongodb_secret_arn" {
  description = "ARN of the MongoDB connection secret"
  value       = aws_secretsmanager_secret.mongodb_url.arn

  depends_on = [aws_secretsmanager_secret.mongodb_url]
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id

  depends_on = [aws_vpc.main]
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  depends_on = [aws_subnet.public_1, aws_subnet.public_2]
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  depends_on = [aws_subnet.private_1, aws_subnet.private_2]
}

output "cloudwatch_log_group_name" {
  description = "Name of CloudWatch log group for ECS"
  value       = aws_cloudwatch_log_group.ecs.name

  depends_on = [aws_cloudwatch_log_group.ecs]
}

output "api_url" {
  description = "URL to access the FastAPI application"
  value       = "http://${aws_lb.main.dns_name}"

  depends_on = [aws_lb.main]
}

output "api_docs_url" {
  description = "URL to access the API documentation (Swagger UI)"
  value       = "http://${aws_lb.main.dns_name}/docs"

  depends_on = [aws_lb.main]
}

output "api_redoc_url" {
  description = "URL to access the API documentation (ReDoc)"
  value       = "http://${aws_lb.main.dns_name}/redoc"

  depends_on = [aws_lb.main]
}

output "health_check_url" {
  description = "URL to check application health"
  value       = "http://${aws_lb.main.dns_name}/health"

  depends_on = [aws_lb.main]
}

# Summary of all important endpoints
output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    api_url         = "http://${aws_lb.main.dns_name}"
    docs_url        = "http://${aws_lb.main.dns_name}/docs"
    health_url      = "http://${aws_lb.main.dns_name}/health"
    ecs_cluster     = aws_ecs_cluster.main.name
    documentdb_host = aws_docdb_cluster.main.endpoint
    region          = var.aws_region
  }

  depends_on = [aws_lb.main, aws_ecs_cluster.main, aws_docdb_cluster.main]
}
