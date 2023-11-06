data "aws_iam_role" "lab" {
    name = "LabRole"
}

data "aws_vpc" "default" {
    default = true
}

data "aws_subnets" "private" {
    filter {
      name = "vpc-id"
      values = [data.aws_vpc.default.id]
    }
}

resource "aws_ecs_cluster" "ticketoverflow" {
  name = "ticketoverflow"
}

resource "aws_ecs_task_definition" "ticketoverflow" {
  family = "ticketoverflow"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = 1024
  memory = 2048
  execution_role_arn = data.aws_iam_role.lab.arn
  task_role_arn = data.aws_iam_role.lab.arn

  container_definitions = <<DEFINITION
  [
    {
        "image": "${aws_ecr_repository.ticketoverflow.repository_url}:latest",
        "cpu": 1024,
        "memory": 2048,
        "name": "ticketoverflow",
        "networkMode": "awsvpc",
        "portMappings": [
            {
                "containerPort": 6400,
                "hostPort": 6400
            }
        ],
        "environment": [
          {
            "name": "AWS_REGION",
            "value": "us-east-1"
          },
          {
            "name": "CELERY_BROKER_URL",
            "value": "sqs://"
          },
          {
            "name": "CELERY_RESULT_BACKEND",
            "value": "dynamodb://"
          },
          {
            "name": "AWS_ACCESS_KEY_ID",
            "value": "${data.template_file.aws_credentials.vars.access_key_id}"
          },
          {
            "name": "AWS_SECRET_ACCESS_KEY",
            "value": "${data.template_file.aws_credentials.vars.secret_access_key}"
          }
        ],
        "command": ["celery", "--app", "ticket_overflow.tasks.hamilton", "worker", "--loglevel=info"],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "/ticketoverflow/ticketoverflow",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs",
                "awslogs-create-group": "true"
            }
        }
    }
  ]
  DEFINITION
}

resource "aws_ecs_service" "ticketoverflow" {
  name = "ticketoverflow"
  cluster = aws_ecs_cluster.ticketoverflow.id
  task_definition = aws_ecs_task_definition.ticketoverflow.arn
  desired_count = 1
  launch_type = "FARGATE"

  network_configuration {
    subnets = data.aws_subnets.private.ids
    security_groups = [aws_security_group.ticketoverflow.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ticketoverflow.arn
    container_name = "ticketoverflow"
    container_port = 6400
  }
}