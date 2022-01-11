#!/bin/bash
# run tf-tf from inside a terragrunt before_hook/plan
#
set -e
set -x

varfile="${1}"
if [[ -n "$varfile" ]]; then
  tf_extra_args="-var-file=${varfile}"
fi

export PATH=$PATH:/usr/local/bin

# a full terraform plan/show cycle is slow, skip it if we have no transformations to do
transformations=$(jq length < transformations.json)

if [ "$transformations" -gt 0 ]; then
  terraform plan -out=plan.out -input=false -lock=false ${tf_extra_args}
  terraform show -json plan.out > plan.json

  tf-tf moved --plan plan.json --transformations transformations.json >> moved.tf
else
  echo "$0: transformations.json is empty, skipping"
  exit 0
fi
