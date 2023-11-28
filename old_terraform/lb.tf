resource "aws_lb_target_group" "ticketoverflow" { 
  name          = "ticketoverflow" 
  port          = 6400 
  protocol      = "HTTP" 
  vpc_id        = aws_security_group.ticketoverflow.vpc_id 
  target_type   = "ip" 
 
  health_check { 
    path                = "/api/v1/concerts/health" 
    port                = "6400" 
    protocol            = "HTTP" 
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
  } 
}

resource "aws_lb" "ticketoverflow" {
  name = "ticketoverflow"
  internal = false
  load_balancer_type = "application"
  subnets = data.aws_subnets.private.ids
  security_groups = [aws_security_group.ticketoverflow.id]
}

resource "aws_lb_listener" "ticketoverflow" {
  load_balancer_arn = aws_lb.ticketoverflow.arn
  port = "80"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.ticketoverflow.arn
  }
}

resource "aws_appautoscaling_target" "ticketoverflow" {
  max_capacity = 4
  min_capacity = 1
  resource_id = "service/ticketoverflow/ticketoverflow"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

resource "aws_appautoscaling_policy" "ticketoverflow-cpu" {
  name = "ticketoverflow-cpu"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.ticketoverflow.resource_id
  scalable_dimension = aws_appautoscaling_target.ticketoverflow.scalable_dimension
  service_namespace = aws_appautoscaling_target.ticketoverflow.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 20
  }
}