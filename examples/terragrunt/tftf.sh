#!/bin/bash
# run tf-tf from inside a terragrunt before_hook
# set -x
terraform plan -out=plan.out > /dev/null
terraform show -json plan.out > plan.json
tf-tf apply --plan plan.json --transformations transformations.json
