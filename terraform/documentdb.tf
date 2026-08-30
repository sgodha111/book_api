# DocumentDB Configuration
# MongoDB-compatible database cluster for the FastAPI application

# DB Subnet Group
resource "aws_docdb_subnet_group" "main" {
  name       = "${var.app_name}-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.app_name}-db-subnet-group"
  }
}

# DocumentDB Cluster
resource "aws_docdb_cluster" "main" {
  cluster_identifier      = "${var.app_name}-cluster"
  engine                  = "docdb"
  master_username         = var.db_username
  master_password         = var.db_password
  database_name           = "books_db"
  backup_retention_period = var.db_backup_retention
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = var.environment != "production"

  # Multi-AZ for high availability
  storage_encrypted = true

  # Network configuration
  db_subnet_group_name            = aws_docdb_subnet_group.main.name
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.main.name
  vpc_security_group_ids          = [aws_security_group.documentdb.id]

  # Cluster settings
  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]
  enable_iam_database_authentication = false

  tags = {
    Name = "${var.app_name}-cluster"
  }

  depends_on = [aws_cloudwatch_log_group.documentdb_audit]
}

# DocumentDB Cluster Parameter Group
resource "aws_docdb_cluster_parameter_group" "main" {
  family      = "docdb4.0"
  name        = "${var.app_name}-cluster-parameters"
  description = "Cluster parameter group for ${var.app_name}"

  # Enable automatic failover
  parameter {
    name  = "enabled_cloudwatch_logs_exports"
    value = "audit,error,general,slowquery"
  }

  tags = {
    Name = "${var.app_name}-cluster-param-group"
  }
}

# DocumentDB Instance 1
resource "aws_docdb_cluster_instance" "primary" {
  cluster_identifier = aws_docdb_cluster.main.id
  identifier         = "${var.app_name}-instance-1"
  instance_class     = "db.t3.small"
  engine              = aws_docdb_cluster.main.engine
  engine_version      = aws_docdb_cluster.main.engine_version

  auto_minor_version_upgrade = true
  monitoring_interval        = 60
  monitoring_role_arn        = aws_iam_role.documentdb_monitoring.arn
  performance_insights_enabled = false

  tags = {
    Name = "${var.app_name}-instance-1"
  }
}

# DocumentDB Instance 2 (Read Replica for HA)
resource "aws_docdb_cluster_instance" "secondary" {
  cluster_identifier = aws_docdb_cluster.main.id
  identifier         = "${var.app_name}-instance-2"
  instance_class     = "db.t3.small"
  engine              = aws_docdb_cluster.main.engine
  engine_version      = aws_docdb_cluster.main.engine_version

  auto_minor_version_upgrade = true
  monitoring_interval        = 60
  monitoring_role_arn        = aws_iam_role.documentdb_monitoring.arn
  performance_insights_enabled = false

  tags = {
    Name = "${var.app_name}-instance-2"
  }
}

# IAM Role for DocumentDB Monitoring
resource "aws_iam_role" "documentdb_monitoring" {
  name = "${var.app_name}-documentdb-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.app_name}-documentdb-monitoring-role"
  }
}

# Attach monitoring policy
resource "aws_iam_role_policy_attachment" "documentdb_monitoring" {
  role       = aws_iam_role.documentdb_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Log Groups for DocumentDB
resource "aws_cloudwatch_log_group" "documentdb_audit" {
  name              = "/aws/docdb/${var.app_name}/audit"
  retention_in_days = 7

  tags = {
    Name = "${var.app_name}-docdb-audit-logs"
  }
}

resource "aws_cloudwatch_log_group" "documentdb_error" {
  name              = "/aws/docdb/${var.app_name}/error"
  retention_in_days = 7

  tags = {
    Name = "${var.app_name}-docdb-error-logs"
  }
}

# Secrets Manager Secret for MongoDB URL
resource "aws_secretsmanager_secret_version" "mongodb_url" {
  secret_id = aws_secretsmanager_secret.mongodb_url.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    engine   = "mongodb"
    host     = aws_docdb_cluster.main.endpoint
    port     = 27017
    dbname   = "books_db"
    url      = "mongodb://${var.db_username}:${var.db_password}@${aws_docdb_cluster.main.endpoint}:27017/books_db?replicaSet=rs0&ssl=true&retryWrites=false"
  })
}

# CloudWatch Alarm for DocumentDB CPU
resource "aws_cloudwatch_metric_alarm" "documentdb_cpu" {
  alarm_name          = "${var.app_name}-documentdb-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/DocDB"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when DocumentDB CPU is high"
  dimensions = {
    DBClusterIdentifier = aws_docdb_cluster.main.id
  }
}

# CloudWatch Alarm for DocumentDB Connections
resource "aws_cloudwatch_metric_alarm" "documentdb_connections" {
  alarm_name          = "${var.app_name}-documentdb-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/DocDB"
  period              = "300"
  statistic           = "Average"
  threshold           = "100"
  alarm_description   = "Alert when DocumentDB connections are high"
  dimensions = {
    DBClusterIdentifier = aws_docdb_cluster.main.id
  }
}
