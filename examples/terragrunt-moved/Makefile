TERRAFORM_REQUIRED_VERSION := 1.1.3
TERRAFORM_INSTALLED_VERSION := $(shell terraform version 2>/dev/null | perl -n -e 'print $$1 if /Terraform v(\d+.\d+.\d+)/')


.PHONY: clean tfenv

test: clean stage1 stage2

tfenv:
	if [ "${TERRAFORM_REQUIRED_VERSION}" != "${TERRAFORM_INSTALLED_VERSION}" ] && command -v tfenv > /dev/null ; then tfenv install ${TERRAFORM_REQUIRED_VERSION} && tfenv use ${TERRAFORM_REQUIRED_VERSION}; fi

stage1: tfenv
	@rm -f terraform.tf
	ln -s terraform.tf-stage1 terraform.tf
	terragrunt init
	terragrunt apply -auto-approve

stage2: tfenv
	@rm -f terraform.tf
	ln -s terraform.tf-stage2 terraform.tf
	# this plan will generate the moved.tf in the .terragrunt-cache tree
	terragrunt plan
	cat moved.tf
	# this should be a no-op as moved.tf will have moved the resources to the new addresses
	terragrunt apply -auto-approve

clean:
	@rm -rf .terraform plan.out plan.json foo.bar .terraform.lock.hcl terraform.tfstate terraform.tfstate.*.backup terraform.tf moved.tf terraform.tfstate.backup

install_tools_macos:
	brew install tfenv
