.PHONY: clean

test: clean stage1 stage2

stage1:
	@rm -f terraform.tf
	ln -s terraform.tf-stage1 terraform.tf
	terraform init
	terraform apply -auto-approve

stage2:
	@rm -f terraform.tf
	ln -s terraform.tf-stage2 terraform.tf
	terraform plan -out=plan.out
	terraform show -json plan.out > plan.json
	tf-tf moved --plan plan.json --transformations transformations.json > moves.tf
	# terraform plan -detailed-exitcode
	terraform apply -auto-approve

clean:
	@rm -rf .terraform plan.out plan.json foo.bar .terraform.lock.hcl terraform.tfstate terraform.tfstate.*.backup terraform.tf moves.tf
