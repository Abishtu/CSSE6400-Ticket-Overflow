variable "aws_access_key" {}

variable "aws_secret_key" {}

output "aws_access_key" {
  value = var.aws_access_key
}

output "aws_secret_key" {
  value = var.aws_secret_key
}

provider "aws" {
  region = "ap-southeast-2"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

# resource "aws_security_group" "ticketoverflow_security" {
#   name        = "allow_ssh"
#   description = "Allow inbound SSH traffic"

#   ingress {
#     from_port = 22
#     to_port   = 22
#     protocol  = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   ingress {
#     from_port = 80
#     to_port = 80
#     protocol = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # EC2 Key Pair
# resource "aws_key_pair" "ticket_overflow_key_pair" {
#   key_name = "ticket_overflow_key_pair"
#   public_key = file("./auth/ticket_overflow_key_pair.pub")
# }

# resource "aws_instance" "ec2_instance" {
#   ami           = "ami-0f5f922f781854672"
#   instance_type = "t3.micro"
#   key_name      = aws_key_pair.ticket_overflow_key_pair.key_name

#     tags = {
#       Name = "TicketOverflow"
#     }

#     vpc_security_group_ids = [aws_security_group.ticketoverflow_security.id]

#   # user_data = <<-EOF
#   #             #!/bin/bash
#   #             sudo yum update -y
#   #             sudo yum install docker git
#   #             sudo service docker start
#   #             sudo usermod -a -G docker ec2-user
#   #             sudo chmod 666 /var/run/docker.sock
#   #             sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
#   #             sudo chmod +x /usr/local/bin/docker-compose
#   #             git clone https://github.com/Abishtu/CSSE6400-Ticket-Overflow.git
#   #             cd ~/CSSE6400-Ticket-Overflow
#   #             docker-compose up --build
#   #             EOF

#   # Use the file provisioner to copy your source files and Docker files
# }
