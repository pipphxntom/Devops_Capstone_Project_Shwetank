variable "namespace" {
  type        = string
  default     = "capstone-devops-prod"
  description = "Kubernetes namespace for FlowForge"
}

variable "db_secret" {
  type        = string
  default     = "demo-secret-change-me"
  sensitive   = true
  description = "Placeholder secret for database credentials"
}
