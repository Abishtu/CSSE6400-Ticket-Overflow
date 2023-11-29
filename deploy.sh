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
  export TF_VAR_aws_secret_key="$secret_key"
done < "$CSV_FILE"

echo $TF_VAR_aws_access_key
echo $TF_VAR_aws_secret_key

terraform init
terraform apply

