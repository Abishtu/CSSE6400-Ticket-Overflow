#!/bin/bash
sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl enable docker.service
sudo systemctl enable docker.socket
sudo systemctl start docker.service
sudo systemctl start docker.socket
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
git clone https://github.com/Abishtu/CSSE6400-Ticket-Overflow.git /home/ec2-user/CSSE6400-Ticket-Overflow
docker-compose -f /home/ec2-user/CSSE6400-Ticket-Overflow/docker-compose.yml up --build