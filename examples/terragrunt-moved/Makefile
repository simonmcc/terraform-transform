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
	# this plan will generate the moved.tf in the .terragrunt-cache tree
	terragrunt plan
	cat moved.tf
	# this should be a no-op as moved.tf will have moved the resources to the new addresses
	terragrunt apply -auto-approve

clean:
	@rm -rf .terraform plan.out plan.json foo.bar .terraform.lock.hcl terraform.tfstate terraform.tfstate.*.backup terraform.tf moved.tf terraform.tfstate.backup
