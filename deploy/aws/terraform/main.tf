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

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name = lower("${var.project}-${var.environment}")
  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

check "expected_aws_account" {
  assert {
    condition = (
      var.expected_aws_account_id == "" ||
      var.expected_aws_account_id == data.aws_caller_identity.current.account_id
    )
    error_message = "Authenticated AWS account does not match expected_aws_account_id."
  }
}

resource "aws_kms_key" "context" {
  description             = "Agent Context Gateway context and audit encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = local.tags
}

resource "aws_kms_alias" "context" {
  name          = "alias/${local.name}-context"
  target_key_id = aws_kms_key.context.key_id
}

resource "aws_s3_bucket" "context" {
  bucket_prefix = "${substr(local.name, 0, 20)}-${substr(sha1(local.name), 0, 8)}-"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "context" {
  bucket                  = aws_s3_bucket.context.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
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
    bucket_key_enabled = true
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
  point_in_time_recovery { enabled = true }
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
  point_in_time_recovery { enabled = true }
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
  point_in_time_recovery { enabled = true }
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.context.arn
  }
  tags = local.tags
}

resource "aws_iam_role" "lambda" {
  name = "${local.name}-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_data" {
  name = "${local.name}-data"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.context.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.context.arn}/sources/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:BatchWriteItem",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = [
          aws_dynamodb_table.context_slices.arn,
          aws_dynamodb_table.context_cache.arn,
          aws_dynamodb_table.audit_events.arn
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.context.arn
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name}"
  retention_in_days = var.log_retention_days
  tags              = local.tags
}

resource "aws_lambda_function" "gateway" {
  function_name    = local.name
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.11"
  handler          = "agent_context_gateway.lambda_handler.handler"
  filename         = var.lambda_package_path
  source_code_hash = var.lambda_package_hash == "" ? null : var.lambda_package_hash
  memory_size      = var.lambda_memory_mb
  timeout          = var.lambda_timeout_seconds

  environment {
    variables = {
      ACG_RUNTIME_MODE         = "aws"
      ACG_CONTEXT_BUCKET       = aws_s3_bucket.context.id
      ACG_CONTEXT_SLICES_TABLE = aws_dynamodb_table.context_slices.name
      ACG_CONTEXT_CACHE_TABLE  = aws_dynamodb_table.context_cache.name
      ACG_AUDIT_EVENTS_TABLE   = aws_dynamodb_table.audit_events.name
      ACG_ALLOWED_TASK_TYPES   = join(",", var.allowed_task_types)
      ACG_MAX_SENSITIVITY      = var.max_sensitivity
      ACG_POLICY_FILE          = "config/policy.json"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy.lambda_data
  ]
  tags = local.tags
}

resource "aws_cognito_user_pool" "gateway" {
  name                     = local.name
  deletion_protection      = var.cognito_deletion_protection
  auto_verified_attributes = []
  tags                     = local.tags
}

resource "aws_cognito_resource_server" "gateway" {
  identifier   = "${local.name}-api"
  name         = "${local.name}-api"
  user_pool_id = aws_cognito_user_pool.gateway.id
  scope {
    scope_name        = "use"
    scope_description = "Call Agent Context Gateway APIs"
  }
}

resource "aws_cognito_user_pool_client" "gateway" {
  name                                 = "${local.name}-client"
  user_pool_id                         = aws_cognito_user_pool.gateway.id
  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_scopes                 = ["${aws_cognito_resource_server.gateway.identifier}/use"]
  enable_token_revocation              = true
  access_token_validity                = 60
  token_validity_units {
    access_token = "minutes"
  }
}

resource "aws_cognito_user_pool_domain" "gateway" {
  domain       = substr(replace("${local.name}-${data.aws_caller_identity.current.account_id}", "_", "-"), 0, 63)
  user_pool_id = aws_cognito_user_pool.gateway.id
}

resource "aws_apigatewayv2_api" "gateway" {
  name          = local.name
  protocol_type = "HTTP"
  dynamic "cors_configuration" {
    for_each = length(var.cors_allow_origins) > 0 ? [1] : []
    content {
      allow_headers = ["authorization", "content-type"]
      allow_methods = ["GET", "POST", "OPTIONS"]
      allow_origins = var.cors_allow_origins
      max_age       = 300
    }
  }
  tags = local.tags
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.gateway.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito"
  jwt_configuration {
    audience = [aws_cognito_user_pool_client.gateway.id]
    issuer   = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${aws_cognito_user_pool.gateway.id}"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.gateway.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.gateway.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 30000
}

resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.gateway.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "capsules" {
  api_id             = aws_apigatewayv2_api.gateway.id
  route_key          = "POST /v1/capsules"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_scopes = [
    "${aws_cognito_resource_server.gateway.identifier}/use"
  ]
}

resource "aws_apigatewayv2_route" "insights" {
  api_id             = aws_apigatewayv2_api.gateway.id
  route_key          = "POST /v1/insights"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_scopes = [
    "${aws_cognito_resource_server.gateway.identifier}/use"
  ]
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.gateway.id
  name        = "$default"
  auto_deploy = true
  tags        = local.tags
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.gateway.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.gateway.execution_arn}/*/*"
}
