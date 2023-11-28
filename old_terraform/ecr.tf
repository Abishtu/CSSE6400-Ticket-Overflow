data "aws_ecr_authorization_token" "ecr_token" {}

provider "docker" {
  registry_auth {
    address = data.aws_ecr_authorization_token.ecr_token.proxy_endpoint
    username = data.aws_ecr_authorization_token.ecr_token.user_name
    password = data.aws_ecr_authorization_token.ecr_token.password
  }
}

resource "aws_ecr_repository" "ticketoverflow" {
  name = "ticketoverflow"
}
# ${aws_ecr_repository.ticketoverflow.name}:latest
resource "docker_image" "ticketoverflow" {
  name = "${aws_ecr_repository.ticketoverflow.repository_url}:latest"
  build {
    context = "."
    dockerfile = "Dockerfile"
  }
  
}

resource "docker_registry_image" "ticketoverflow" {
  name = docker_image.ticketoverflow.name
}