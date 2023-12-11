variable "aws_access_key" {
  type = string
}

variable "aws_secret_key" {
  type = string
}

variable "keyname" {
 type = string
 default = "default_new_key"
}

provider "aws" {
  region = "ap-southeast-2"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}

resource "tls_private_key" "ticket_overflow_key" {
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "local_file" "ticket_overflow_private_key" {
  content = tls_private_key.ticket_overflow_key.private_key_pem
  filename = "./auth/ticket_overflow_private_key.pem"
  file_permission = 0400
}

resource "aws_key_pair" "ticket_overflow_key_pair" {
  key_name = "ticket_overflow_key_pair"
  public_key = tls_private_key.ticket_overflow_key.public_key_openssh
}

resource "aws_security_group" "ticket_overflow_security_group" {
  name = "ticket_overflow_security_group"
  description = "Allows HTTP, port 80 and SSH, port 22 connections"
  
  ingress {
    description = "HTTP"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
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
}

resource "aws_instance" "ec2_instance" {
  ami = "ami-0f5f922f781854672"
  instance_type = "t3.micro"
  key_name = aws_key_pair.ticket_overflow_key_pair.key_name
  
  
  tags = {
    Name = "TicketOverflow"
  }

  vpc_security_group_ids = [ aws_security_group.ticket_overflow_security_group.id ]
  user_data = file("./app_install.sh")
}