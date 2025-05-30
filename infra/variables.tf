variable "vpc_id" {
  description = "The VPC in which to create resources"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnets for the ALB & Fargate tasks"
  type        = list(string)
}

variable "api_image_uri" {
  description = "ECR image URI for the API container"
  type        = string
}

variable "database_url" {
  description = "Connection string for Postgres"
  type        = string
}

variable "jwt_secret" {
  description = "JWT secret for the API"
  type        = string
}

variable "api_auth_user" {
  description = "Basic auth username for the API"
  type        = string
}

variable "api_auth_pass" {
  description = "Basic auth password for the API"
  type        = string
}
