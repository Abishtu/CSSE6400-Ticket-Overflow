#!/bin/bash

AWS_ACCESS_KEY="${var.aws_access_key}"
AWS_SECRET_KEY="${var.aws_secret_key}"
AWS_REGION="ap-southeast-2"

sudo yum update -y
sudo yum install -y docker git aws-cli
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl enable docker.service
sudo systemctl enable docker.socket
sudo systemctl start docker.service
sudo systemctl start docker.socket
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Set up AWS CLI
aws configure set aws_access_key_id $AWS_ACCESS_KEY
aws configure set aws_secret_access_key $AWS_SECRET_KEY
aws configure set default.region $AWS_REGION

git clone --branch terraform_deployment https://github.com/Abishtu/CSSE6400-Ticket-Overflow.git /home/ec2-user/CSSE6400-Ticket-Overflow
docker-compose -f /home/ec2-user/CSSE6400-Ticket-Overflow/docker-compose.yml up --build