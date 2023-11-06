#!/bin/bash

terraform init
terraform apply -auto-approve

terraform output ticketoverflow_api_url | awk '{print "http://"$1}' | sed 's/"//g' > "api.txt"
