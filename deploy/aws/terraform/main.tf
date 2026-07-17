terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name = "${var.project}-${var.environment}"
  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_key" "context" {
  description             = "KMS key for Agent Context Gateway context slices and audit artifacts"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = local.tags
}

resource "aws_kms_alias" "context" {
  name          = "alias/${local.name}-context"
  target_key_id = aws_kms_key.context.key_id
}

resource "aws_s3_bucket" "context" {
  bucket_prefix = "${local.name}-context-"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_versioning" "context" {
  bucket = aws_s3_bucket.context.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "context" {
  bucket = aws_s3_bucket.context.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.context.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_dynamodb_table" "context_slices" {
  name         = "${local.name}-context-slices"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "slice_id"

  attribute {
    name = "slice_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.context.arn
  }

  tags = local.tags
}

resource "aws_dynamodb_table" "context_cache" {
  name         = "${local.name}-context-cache"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "cache_key"

  attribute {
    name = "cache_key"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.context.arn
  }

  tags = local.tags
}

resource "aws_dynamodb_table" "audit_events" {
  name         = "${local.name}-audit-events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "audit_id"

  attribute {
    name = "audit_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.context.arn
  }

  tags = local.tags
}

resource "aws_ecr_repository" "gateway" {
  name                 = local.name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.context.arn
  }

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "gateway" {
  name              = "/aws/ecs/${local.name}"
  retention_in_days = 30
  tags              = local.tags
}

resource "aws_ecs_cluster" "gateway" {
  name = local.name
  tags = local.tags
}

resource "aws_iam_role" "task_execution" {
  name = "${local.name}-task-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "gateway_task" {
  name = "${local.name}-gateway-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
  tags = local.tags
}

resource "aws_iam_policy" "gateway_task" {
  name = "${local.name}-gateway-task"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.context.arn,
          "${aws_s3_bucket.context.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.context_slices.arn,
          aws_dynamodb_table.context_cache.arn,
          aws_dynamodb_table.audit_events.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.context.arn
      }
    ]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "gateway_task" {
  role       = aws_iam_role.gateway_task.name
  policy_arn = aws_iam_policy.gateway_task.arn
}
