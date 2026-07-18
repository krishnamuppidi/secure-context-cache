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
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "expected_aws_account_id" {
  description = "Optional safety guard. Deployment fails if credentials target another account."
  type        = string
  default     = ""
}

variable "lambda_package_path" {
  description = "Absolute path to the deployment ZIP built by deploy.sh."
  type        = string
  default     = "../../../build/acg-lambda.zip"
}

variable "lambda_package_hash" {
  description = "Base64 SHA-256 of the deployment ZIP."
  type        = string
  default     = ""
}

variable "lambda_memory_mb" {
  description = "Lambda memory in MB."
  type        = number
  default     = 1024
}

variable "lambda_timeout_seconds" {
  description = "Lambda timeout. API Gateway has a 30-second integration limit."
  type        = number
  default     = 29
}

variable "log_retention_days" {
  description = "CloudWatch log retention."
  type        = number
  default     = 30
}

variable "allowed_task_types" {
  description = "Task profiles granted to the generated Cognito machine client."
  type        = list(string)
  default     = ["code_review", "iac_security", "incident_triage", "onboarding", "architecture_qa"]
}

variable "max_sensitivity" {
  description = "Maximum sensitivity released to the generated machine client."
  type        = string
  default     = "high"
  validation {
    condition     = contains(["low", "medium", "high"], var.max_sensitivity)
    error_message = "max_sensitivity must be low, medium, or high."
  }
}

variable "cors_allow_origins" {
  description = "Browser origins allowed by the HTTPS API. Keep restrictive for production."
  type        = list(string)
  default     = []
}

variable "cognito_deletion_protection" {
  description = "Use ACTIVE for long-lived deployments after initial evaluation."
  type        = string
  default     = "INACTIVE"
  validation {
    condition     = contains(["ACTIVE", "INACTIVE"], var.cognito_deletion_protection)
    error_message = "cognito_deletion_protection must be ACTIVE or INACTIVE."
  }
}
