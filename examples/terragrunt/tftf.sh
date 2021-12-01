#!/bin/bash
# run tftf from inside a terragrunt before_hook
# set -x
terraform plan -out=plan.out > /dev/null
terraform show -json plan.out > plan.json
tftf apply --plan plan.json --transformations transformations.json
