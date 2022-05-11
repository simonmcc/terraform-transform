TERRAFORM_REQUIRED_VERSION := 1.1.3
TERRAFORM_INSTALLED_VERSION := $(shell terraform version 2>/dev/null | perl -n -e 'print $$1 if /Terraform v(\d+.\d+.\d+)/')

test: clean stage1 stage2

tfenv:
	if [ "${TERRAFORM_REQUIRED_VERSION}" != "${TERRAFORM_INSTALLED_VERSION}" ] && command -v tfenv > /dev/null ; then tfenv install ${TERRAFORM_REQUIRED_VERSION} && tfenv use ${TERRAFORM_REQUIRED_VERSION}; fi


stage1:
	@rm -f terraform.tf
	ln -s terraform.tf-stage1 terraform.tf
	terragrunt init
	terragrunt apply -auto-approve

stage2:
	@rm -f terraform.tf
	ln -s terraform.tf-stage2 terraform.tf
	terragrunt apply -auto-approve

clean:
	@rm -rf .terraform plan.out plan.json foo.bar .terraform.lock.hcl terraform.tfstate terraform.tfstate.*.backup terraform.tf
