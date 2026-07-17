variable "project" {
  description = "Project name used for resource naming."
  type        = string
  default     = "agent-context-gateway"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the demo VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks for the plug-and-play Fargate deployment."
  type        = list(string)
  default     = ["10.42.1.0/24", "10.42.2.0/24"]
}

variable "allowed_http_cidrs" {
  description = "CIDR blocks allowed to reach the public ALB. Set explicitly for demos; do not use 0.0.0.0/0 for production."
  type        = list(string)
  default     = ["127.0.0.1/32"]
}

variable "container_port" {
  description = "Container port exposed by the gateway."
  type        = number
  default     = 8080
}

variable "desired_count" {
  description = "Number of ECS tasks."
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Fargate CPU units."
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Fargate memory in MiB."
  type        = number
  default     = 1024
}

variable "image_tag" {
  description = "Image tag to deploy from ECR."
  type        = string
  default     = "latest"
}

variable "health_check_path" {
  description = "Gateway health check path."
  type        = string
  default     = "/health"
}
