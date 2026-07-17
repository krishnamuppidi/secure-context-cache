output "context_bucket" {
  value = aws_s3_bucket.context.id
}

output "kms_key_arn" {
  value = aws_kms_key.context.arn
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

output "ecr_repository_url" {
  value = aws_ecr_repository.gateway.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.gateway.name
}

output "alb_dns_name" {
  value = aws_lb.gateway.dns_name
}

output "app_url" {
  value = "http://${aws_lb.gateway.dns_name}"
}

output "health_url" {
  value = "http://${aws_lb.gateway.dns_name}/health"
}
