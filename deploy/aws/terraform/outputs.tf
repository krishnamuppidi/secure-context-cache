output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  value = data.aws_region.current.region
}

output "api_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "health_url" {
  value = "${aws_apigatewayv2_stage.default.invoke_url}/health"
}

output "context_bucket" {
  value = aws_s3_bucket.context.id
}

output "context_slices_table" {
  value = aws_dynamodb_table.context_slices.name
}

output "context_cache_table" {
  value = aws_dynamodb_table.context_cache.name
}

output "audit_events_table" {
  value = aws_dynamodb_table.audit_events.name
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.gateway.id
}

output "cognito_client_secret" {
  value     = aws_cognito_user_pool_client.gateway.client_secret
  sensitive = true
}

output "cognito_scope" {
  value = "${aws_cognito_resource_server.gateway.identifier}/use"
}

output "cognito_token_url" {
  value = "https://${aws_cognito_user_pool_domain.gateway.domain}.auth.${data.aws_region.current.region}.amazoncognito.com/oauth2/token"
}

output "lambda_function_name" {
  value = aws_lambda_function.gateway.function_name
}
