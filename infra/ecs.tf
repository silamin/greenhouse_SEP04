provider "aws" {
  region = "eu-north-1"
}

###############################################################################
# 1) ALB SECURITY GROUP
###############################################################################
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
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

###############################################################################
# 2) ECS SG (FOR API CONTAINERS)
###############################################################################
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

###############################################################################
# 3) API ALB + TG + LISTENER
###############################################################################
resource "aws_lb" "api_alb" {
  name               = "api-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb_sg.id]
}

resource "aws_lb_target_group" "api_tg" {
  name        = "api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
}

resource "aws_lb_listener" "api_listener" {
  load_balancer_arn = aws_lb.api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_tg.arn
  }
}

###############################################################################
# 4) ECS CLUSTER
###############################################################################
resource "aws_ecs_cluster" "api_cluster" {
  name = "greenhouse-cluster"
}

###############################################################################
# 5) EXECUTION ROLE + SSM/KMS POLICY
###############################################################################
data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_exec_role" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

resource "aws_iam_role_policy_attachment" "exec_policy" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_caller_identity" "current" {}

resource "aws_iam_policy" "ssm_kms_access" {
  name = "ecs_ssm_kms_read_access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/*"
      },
      {
        Effect = "Allow"
        Action = ["kms:Decrypt"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_kms_attach" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = aws_iam_policy.ssm_kms_access.arn
}

###############################################################################
# 6) ECS TASK DEFINITION (API)
###############################################################################
resource "aws_ecs_task_definition" "api_task" {
  family                   = "api-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn

  container_definitions = jsonencode([

    # ─── Postgres container ───────────────────────────────────────────
    {
      name         = "postgres"
      image        = "postgres:15"
      essential    = true
      mountPoints  = [{ sourceVolume = "pgdata", containerPath = "/var/lib/postgresql/data" }]
      portMappings = [{ containerPort = 5432, protocol = "tcp" }]

      # only non-sensitive ENV here
      environment = [
        { name = "PGDATA", value = "/var/lib/postgresql/data" }
      ]

      # secrets must live under `secrets`
      secrets = [
        {
          name      = "POSTGRES_USER"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/pg_user"
        },
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/pg_password"
        },
        {
          name      = "POSTGRES_DB"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/pg_db"
        }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
        interval    = 5
        timeout     = 2
        retries     = 5
        startPeriod = 10
      }

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/api-service"
          "awslogs-region"        = "eu-north-1"
          "awslogs-stream-prefix" = "postgres"
          "awslogs-create-group"  = "true"
        }
      }
    },

    # ─── API container ─────────────────────────────────────────────────
    {
      name         = "api-service"
      image        = var.api_image_uri
      essential    = true
      dependsOn    = [{ containerName = "postgres", condition = "HEALTHY" }]
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://127.0.0.1:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/database_url"
        },
        {
          name      = "JWT_SECRET"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/jwt_secret"
        },
        {
          name      = "API_AUTH_USER"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/api_auth_user"
        },
        {
          name      = "API_AUTH_PASS"
          valueFrom = "arn:aws:ssm:eu-north-1:${data.aws_caller_identity.current.account_id}:parameter/api/api_auth_pass"
        }
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

  volume {
    name = "pgdata"
  }
}

###############################################################################
# 7) ECS SERVICE (API)
###############################################################################
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
    aws_lb_listener.api_listener,
  ]
}

###############################################################################
# 8) FRONTEND SECURITY GROUP (ALLOW FROM ALB)
###############################################################################
resource "aws_security_group" "frontend_sg" {
  name        = "frontend-sg"
  description = "Allow traffic from ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 3000
    to_port         = 3000
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

###############################################################################
# 9) FRONTEND ALB + TG + LISTENER
###############################################################################
resource "aws_lb" "frontend_alb" {
  name               = "frontend-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb_sg.id]
}

resource "aws_lb_target_group" "frontend_tg" {
  name        = "frontend-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200-399"
  }
}

resource "aws_lb_listener" "frontend_listener" {
  load_balancer_arn = aws_lb.frontend_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend_tg.arn
  }
}

###############################################################################
# 10) ECS TASK DEFINITION (FRONTEND)
###############################################################################
resource "aws_ecs_task_definition" "frontend_task" {
  family                   = "frontend-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn

  container_definitions = jsonencode([[
    {
      "name"         = "frontend-service",
      "image"        = "${var.frontend_image_uri}",
      "essential"    = true,
      "portMappings" = [{ "containerPort" = 3000, "protocol" = "tcp" }],
      "environment"  = [
        {
          "name"  = "API_URL",
          "value" = "http://${aws_lb.api_alb.dns_name}"
        }
      ],
      "healthCheck" = {
        "command"     = ["CMD-SHELL", "curl -f http://localhost:3000/ || exit 1"],
        "interval"    = 30,
        "timeout"     = 5,
        "retries"     = 3,
        "startPeriod" = 15
      },
      "logConfiguration" = {
        "logDriver" = "awslogs",
        "options" = {
          "awslogs-group"         = "/ecs/frontend-service",
          "awslogs-region"        = "eu-north-1",
          "awslogs-stream-prefix" = "ecs",
          "awslogs-create-group"  = "true"
        }
      }
    }
  ]])
}

###############################################################################
# 11) ECS SERVICE (FRONTEND)
###############################################################################
resource "aws_ecs_service" "frontend_svc" {
  name            = "frontend-service"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.frontend_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.frontend_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend_tg.arn
    container_name   = "frontend-service"
    container_port   = 3000
  }

  depends_on = [
    aws_lb_listener.frontend_listener
  ]
}

###############################################################################
# 12) SG FOR ONE-SHOT ML JOB (OUTBOUND-ONLY)
###############################################################################
resource "aws_security_group" "ml_sg" {
  name        = "ml-sg"
  description = "Security group for scheduled ML retrain"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

###############################################################################
# 13) ECS TASK DEFINITION (ML RETRAIN)
###############################################################################
resource "aws_ecs_task_definition" "ml_retrain" {
  family                   = "ml-retrain"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn

  container_definitions = jsonencode([[
    {
      "name"      = "ml-retrain",
      "image"     = "${var.ml_image_uri}",
      "essential" = true,
      "command"   = ["bash", "-c", "python -m src.train && aws s3 cp model.joblib s3://${var.model_bucket}/model.joblib"],
      "environment" = [
        { "name" = "AWS_REGION", "value" = "eu-north-1" }
      ],
      "logConfiguration" = {
        "logDriver" = "awslogs",
        "options" = {
          "awslogs-group"         = "/ecs/ml-retrain",
          "awslogs-region"        = "eu-north-1",
          "awslogs-stream-prefix" = "ecs",
          "awslogs-create-group"  = "true"
        }
      }
    }
  ]])
}

###############################################################################
# 14) ALLOW THE TASK TO PUT THE REFRESHED MODEL TO S3
###############################################################################
resource "aws_iam_policy" "s3_upload_model" {
  name = "ecs_s3_upload_model"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:PutObject"],
        Resource = "arn:aws:s3:::${var.model_bucket}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3_upload" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = aws_iam_policy.s3_upload_model.arn
}

###############################################################################
# 15) EVENTBRIDGE RULE – ONCE PER DAY AT 02:00 UTC
###############################################################################
resource "aws_cloudwatch_event_rule" "ml_retrain_cron" {
  name                = "ml-retrain-daily"
  schedule_expression = "cron(0 2 * * ? *)"
}

###############################################################################
# A) IAM ROLE FOR EVENTBRIDGE TO INVOKE ECS
###############################################################################
data "aws_iam_policy_document" "eventbridge_run_ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eventbridge_ecs_run_role" {
  name               = "eventbridge-ecs-run-role"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_run_ecs_assume.json
}

resource "aws_iam_role_policy" "eventbridge_ecs_run_policy" {
  name = "allow-eventbridge-to-run-ecs"
  role = aws_iam_role.eventbridge_ecs_run_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["ecs:RunTask"],
        Resource = [
          "arn:aws:ecs:eu-north-1:${data.aws_caller_identity.current.account_id}:task-definition/ml-retrain:*"
        ]
      },
      {
        Effect = "Allow",
        Action = ["iam:PassRole"],
        Resource = [
          aws_iam_role.ecs_task_exec_role.arn
        ]
      }
    ]
  })
}

###############################################################################
# B) UPDATE THE EVENTBRIDGE TARGET TO USE THE NEW ROLE
###############################################################################
resource "aws_cloudwatch_event_target" "ml_retrain_target" {
  rule      = aws_cloudwatch_event_rule.ml_retrain_cron.name
  target_id = "RunMLRetrain"
  arn       = aws_ecs_cluster.api_cluster.arn
  role_arn  = aws_iam_role.eventbridge_ecs_run_role.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.ml_retrain.arn
    launch_type         = "FARGATE"
    platform_version    = "1.4.0"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [aws_security_group.ml_sg.id]
      assign_public_ip = true
    }
  }
}