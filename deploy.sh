#!/bin/bash

# Specify the path to your CSV file
CSV_FILE="./auth/credentials.csv"

# Check if the CSV file exists
if [ ! -f "$CSV_FILE" ]; then
  echo "CSV file not found: $CSV_FILE"
  exit 1
fi

# Read the CSV file and set environment variables
while IFS=, read -r access_key secret_key; do
  export TF_VAR_aws_access_key="$access_key"
  export TF_VAR_aws_secret_key=$(echo $secret_key | sed 's/\r$//')
done < "$CSV_FILE"

#terraform init
#terraform apply

if [ "$1" == "--build" ];then
  terraform init
  terraform apply
elif [ "$1" == "--destroy" ];then
  terraform destroy
elif [ "$1" == "--local" ]; then
  export AWS_ACCESS_KEY=$TF_VAR_aws_access_key
  export AWS_SECRET_KEY=$TF_VAR_aws_secret_key
  export AWS_REGION="ap-southeast-2"

#   aws configure --profile workshop set aws_access_key_id $AWS_ACCESS_KEY
#   aws configure --profile workshop set aws_secret_access_key $AWS_SECRET_KEY
#   aws configure --profile workshop default.region $AWS_REGION

  docker-compose down --volumes
  docker-compose up --build
fi
