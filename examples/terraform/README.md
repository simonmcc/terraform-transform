# terraform example

Worked example of avoiding a `local_file` destroy/create cycle by matching filename & content to discover new tfstate address.

We simulate a terraform evolution by creating a file in stage 1 & then in stage 2 changing the resource name, but not the filename or content (i.e. a resource has moved from a root project into a module, but is other wise unchanged)

Running `make` should run through this whole process, which we break down here:

## Stage 1 - create the resource & tfstate
```bash
Terraform will perform the following actions:

  # local_file.stage1 will be created
  + resource "local_file" "stage1" {
      + content              = "foo!"
      + directory_permission = "0777"
      + file_permission      = "0777"
      + filename             = "./foo.bar"
      + id                   = (known after apply)
    }

  # random_pet.petname will be created
  + resource "random_pet" "petname" {
      + id        = (known after apply)
      + length    = 5
      + separator = "-"
    }

Plan: 2 to add, 0 to change, 0 to destroy.
local_file.stage1: Creating...
random_pet.petname: Creating...
local_file.stage1: Creation complete after 0s [id=4bf3e335199107182c6f7638efaad377acc7f452]
random_pet.petname: Creation complete after 0s [id=endlessly-largely-urgently-driven-magpie]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

## Stage 2 - rename the terraform resource

Terraform now shows a destroy/create cycle, for a file on disk that hasn't changed:

```bash
ln -s terraform.tf-stage2 terraform.tf
terraform plan -out=plan.out
local_file.stage1: Refreshing state... [id=4bf3e335199107182c6f7638efaad377acc7f452]
random_pet.petname: Refreshing state... [id=endlessly-largely-urgently-driven-magpie]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
  - destroy

Terraform will perform the following actions:

  # local_file.stage1 will be destroyed
  - resource "local_file" "stage1" {
      - content              = "foo!" -> null
      - directory_permission = "0777" -> null
      - file_permission      = "0777" -> null
      - filename             = "./foo.bar" -> null
      - id                   = "4bf3e335199107182c6f7638efaad377acc7f452" -> null
    }

  # local_file.stage2 will be created
  + resource "local_file" "stage2" {
      + content              = "foo!"
      + directory_permission = "0777"
      + file_permission      = "0777"
      + filename             = "./foo.bar"
      + id                   = (known after apply)
    }

Plan: 1 to add, 0 to change, 1 to destroy.

Saved the plan to: plan.out
```

`tf-tf` needs the json plan output:

```bash
terraform show -json plan.out > plan.json
```

We now run `tf-tf` with this as the contents of  `transformations.json`:

```json
[
  {
    "source": "[?type == 'local_file'].{address: address, change: change.before.{filename:filename, content:content}}",
    "target": "[?type == 'local_file'].{address: address, change: change.after.{filename:filename, content:content}}"
  }
]
```

This single transformation will identify any `local_file` resources that match based on the `filename` & `content` keys in the `change` plan.

```bash
tf-tf apply --plan plan.json --transformations transformations.json
action is apply
Executing `terraform state mv local_file.stage1 local_file.stage2`
Move "local_file.stage1" to "local_file.stage2"
Successfully moved 1 object(s).
```

The terraform state is now in-sync with the current plan, so re-running plan will result in `No changes`.

```bash
terraform plan -detailed-exitcode
local_file.stage2: Refreshing state... [id=4bf3e335199107182c6f7638efaad377acc7f452]
random_pet.petname: Refreshing state... [id=endlessly-largely-urgently-driven-magpie]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
```
