terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 4.0"
        }
        docker = {
            source = "kreuzwerker/docker"
            version = "3.0.2"
        }
    }
}

provider "aws" {
    region = "us-east-1"
    shared_credentials_files = ["./credentials"]
    default_tags {
        tags = {
            Course       = "CSSE6400"
            Name         = "TicketOverflow"
            Automation   = "Terraform"
        }
    }
}

data "template_file" "aws_credentials" {
  template = "${file("${path.module}/credentials")}"

  vars = {
    access_key_id = "${split("=", split("\n", file("${path.module}/credentials"))[1])[1]}"
    secret_access_key = "${split("=", split("\n", file("${path.module}/credentials"))[2])[1]}"
  }
}

resource "aws_security_group" "ticketoverflow" {
  name = "ticketoverflow"
  description = "TicketOverflow Security Group"

  ingress {
    from_port = 6400
    to_port = 6400
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "ticketoverflow_api_url" {
  value = aws_lb.ticketoverflow.dns_name
}