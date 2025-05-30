provider "aws" {
  region = "eu-north-1"
}

# 1) Security Group for ALB
resource "aws_security_group" "alb_sg" {
  name        = "ecs-services-sg"
  description = "Allow ports 8000, 3000, 9000 for ECS services"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2) Security Group for ECS tasks
resource "aws_security_group" "ecs_sg" {
  name        = "ecs-sg"
  description = "Allow traffic from ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3) Application Load Balancer
resource "aws_lb" "api_alb" {
  name               = "api-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb_sg.id]

  # Optional tuning
  idle_timeout                         = 60
  enable_http2                         = true
  desync_mitigation_mode               = "defensive"
  enable_cross_zone_load_balancing     = true

  lifecycle {
    ignore_changes = [
      # AWS‐generated; keep Terraform from diffing these
      dns_name,
      arn_suffix,
      zone_id,
      id,
    ]
  }
}

# 3a) Target Group (imported)
resource "aws_lb_target_group" "api_tg" {
  name        = "api-service-tg"  # matches existing
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = 8000
    interval            = 30
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
    matcher             = "200"
  }
}

# 3b) Listener
resource "aws_lb_listener" "api_listener" {
  load_balancer_arn = aws_lb.api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_tg.arn
  }
}

# 4) ECS Cluster
resource "aws_ecs_cluster" "api_cluster" {
  name = "api-cluster"
}

# 5) Existing Execution Role
data "aws_iam_role" "ecs_task_exec_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_iam_role_policy_attachment" "exec_policy" {
  role       = data.aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 6) Task Definition
resource "aws_ecs_task_definition" "api_task" {
  family                   = "api-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = data.aws_iam_role.ecs_task_exec_role.arn

  container_definitions = jsonencode([
    {
      name      = "api-service"
      image     = var.api_image_uri
      essential = true
      portMappings = [
        { containerPort = 8000, protocol = "tcp" }
      ]
      environment = [
        { name = "DATABASE_URL",  value = var.database_url  },
        { name = "JWT_SECRET",    value = var.jwt_secret    },
        { name = "API_AUTH_USER", value = var.api_auth_user },
        { name = "API_AUTH_PASS", value = var.api_auth_pass },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/api-service"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# 7) ECS Service
resource "aws_ecs_service" "api_svc" {
  name            = "api-service"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.api_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_tg.arn
    container_name   = "api-service"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.api_listener
  ]
}
