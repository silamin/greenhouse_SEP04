# terraform.tfvars

vpc_id             = "vpc-097beff0168000026"
subnet_ids         = [
  "subnet-0b9fe726f5489df47",
  "subnet-0cf9f3e15c1cac4d1",
  "subnet-0e5436a76e48f4a6f",
]

api_image_uri      = "067826606836.dkr.ecr.eu-north-1.amazonaws.com/api-service:YOUR_TAG"
frontend_image_uri = "067826606836.dkr.ecr.eu-north-1.amazonaws.com/frontend-service:YOUR_TAG"
ml_image_uri = "067826606836.dkr.ecr.eu-north-1.amazonaws.com/ml-retrain:YOUR_TAG"
model_bucket = "greenhouse-ml-artifacts"
