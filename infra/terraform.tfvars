vpc_id        = "vpc-097beff0168000026"
subnet_ids    = [
  "subnet-0b9fe726f5489df47",
  "subnet-0cf9f3e15c1cac4d1",
  "subnet-0e5436a76e48f4a6f",
]
api_image_uri = "067826606836.dkr.ecr.eu-north-1.amazonaws.com/api-service:YOUR_TAG"
database_url  = "postgresql://postgres:postgres@postgres:5432/greenhouse"
jwt_secret    = "dev-secret-change-me"
api_auth_user = "tcp_worker"
api_auth_pass = "supersecret"
