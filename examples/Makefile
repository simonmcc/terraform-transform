.PHONY: clean

test: clean stage1 stage2

stage1:
	@rm -f terraform.tf
	ln -s terraform.tf-stage1 terraform.tf
	terragrunt init
	terragrunt apply -auto-approve

stage2:
	@rm -f terraform.tf
	ln -s terraform.tf-stage2 terraform.tf
	terragrunt plan -out=plan.out
	terragrunt show -json plan.out > plan.json
	tftf apply --plan plan.json --transformations transformations.json
	terraform plan -detailed-exitcode

clean:
	@rm -rf .terraform plan.out plan.json .terraform.lock.hcl terraform.tfstate terraform.tfstate.*.backup
