# variables.tf

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

variable "frontend_image_uri" {
  description = "ECR image URI for the Frontend container"
  type        = string
}

variable "ml_image_uri" {
  description = "ECR image URI for the ML retrain container"
  type        = string
}
variable "model_bucket" {
  description = "S3 bucket where the refreshed model is stored"
  type        = string
}
