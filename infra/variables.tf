variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project" {
  description = "Name prefix for all resources"
  type        = string
  default     = "risk-classifier"
}

variable "github_owner" {
  description = "GitHub user or org owning the repo"
  type        = string
  default     = "eddayyy"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "client-risk-classifier"
}

variable "github_oauth_token" {
  description = "GitHub OAuth token (with repo:read and webhook permissions)"
  type        = string
  sensitive   = true
}

variable "node_group_desired_capacity" {
  description = "Desired number of worker nodes in EKS"
  type        = number
  default     = 2
}

variable "node_group_instance_types" {
  description = "Instance types for EKS nodes"
  type        = list(string)
  default     = ["t3.medium"]
}
