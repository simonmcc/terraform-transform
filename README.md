# Terraform Transform

This tool will parse a Terraform plan file and `terraform state mv` resources that would normally be deleted & re-created.

It can also be used to generate Terraform >=1.1 `moved` statements for non-trivial moves (e.g. when the index of a resource address has changed)

Arbitrary delete/re-create cycles can be prevented by moving the resources to their new address in terraform state, avoiding the delete/recreate.

Potential source & target addresses are identified by JMESPath queries applied to the [Terraform Plan
Representation](https://www.terraform.io/docs/internals/json-format.html#plan-representation)

Inspired by

* https://github.com/bcochofel/terraplanfeed
* https://github.com/aleksanderaleksic/tgmigrate
* https://github.com/minamijoyo/tfmigrate

## `local_file` example

There is a complete `local_file` example in [examples/terraform](examples/terraform), and a `Makefile` used to simulate avoiding a destroy/create cycle by manipulating the terraform state. There's also a [terragrunt](https://terragrunt.gruntwork.io/) [example](examples/terraform) where tf-tf is executed as part of a `before_hook`.

Example execution:

```bash
terraform plan -out=plan.out
terraform show -json plan.out > plan.json
tf-tf apply --plan plan.json --transformations transformations.json
# tf-tf will then execute required `terraform state mv` commands
Executing `terraform state mv local_file.stage1 local_file.stage2`
Move "local_file.stage1" to "local_file.stage2"
Successfully moved 1 object(s).
```

## Detailed real-world example

Given:

```hcl
# azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"] will be destroyed
- resource "azurerm_private_dns_a_record" "legacy_vm" {
    - fqdn                = "peu1ew1labd001.eu1.taservs.net." -> null
    - id                  = "/subscriptions/b18521cb-9832-4f5c-828a-e8e117818cb5/resourceGroups/eu1-core/providers/Microsoft.Network/privateDnsZones/eu1.taservs.net/A/peu1ew1labd001" -> null
    - name                = "peu1ew1labd001" -> null
    - records             = [
        - "10.10.1.90",
      ] -> null
    - resource_group_name = "eu1-core" -> null
    - tags                = {} -> null
    - ttl                 = 300 -> null
    - zone_name           = "eu1.taservs.net" -> null
  }
```

Which is moving to:

```hcl
# module.taservs_net["eu1.taservs.net"].azurerm_private_dns_a_record.legacy_vm["i-07f551c18b449b591"] will be created
+ resource "azurerm_private_dns_a_record" "legacy_vm" {
    + fqdn                = (known after apply)
    + id                  = (known after apply)
    + name                = "peu1ew1labd001"
    + records             = [
        + "10.10.1.90",
      ]
    + resource_group_name = "eu1-core"
    + ttl                 = 300
    + zone_name           = "eu1.taservs.net"
  }
```

We need to generate the following to avoid the destroy/create cycle:

```
terraform state mv azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"] \
     module.taservs_net["eu1.taservs.net"].azurerm_private_dns_a_record.legacy_vm["i-07f551c18b449b591"]
```

There is no easy search/replace in this example - as the DNS record's tfstate address is changing from a static list to being derived from the instance id.

In the `terraform plan` json output, the `resource_changes` list has entries like this:

```json
    {
      "address": "azurerm_private_dns_a_record.legacy_vm[\"peu1ew1labd001\"]",
      "mode": "managed",
      "type": "azurerm_private_dns_a_record",
      "name": "legacy_vm",
      "index": "peu1ew1labd001",
      "provider_name": "registry.terraform.io/hashicorp/azurerm",
      "change": {
        "actions": [
          "delete"
        ],
        "before": {
          "fqdn": "peu1ew1labd001.eu1.taservs.net.",
          "id": "/subscriptions/b18521cb-9832-4f5c-828a-e8e117818cb5/resourceGroups/eu1-core/providers/Microsoft.Network/privateDnsZones/eu1.taservs.net/A/peu1ew1labd001",
          "name": "peu1ew1labd001",
          "records": [
            "10.10.1.90"
          ],
          "resource_group_name": "eu1-core",
          "tags": {},
          "timeouts": null,
          "ttl": 300,
          "zone_name": "eu1.taservs.net"
        },
        "after": null,
        "after_unknown": {},
        "before_sensitive": {
          "records": [
            false
          ],
          "tags": {}
        },
        "after_sensitive": false
      }
    },
    {
      "address": "module.taservs_net[\"eu1.taservs.net\"].azurerm_private_dns_a_record.legacy_vm[\"i-07f551c18b449b591\"]",
      "module_address": "module.taservs_net[\"eu1.taservs.net\"]",
      "mode": "managed",
      "type": "azurerm_private_dns_a_record",
      "name": "legacy_vm",
      "index": "i-07f551c18b449b591",
      "provider_name": "registry.terraform.io/hashicorp/azurerm",
      "change": {
        "actions": [
          "create"
        ],
        "before": null,
        "after": {
          "name": "peu1ew1labd001",
          "records": [
            "10.10.1.90"
          ],
          "resource_group_name": "eu1-core",
          "tags": null,
          "timeouts": null,
          "ttl": 300,
          "zone_name": "eu1.taservs.net"
        },
        "after_unknown": {
          "fqdn": true,
          "id": true,
          "records": [
            false
          ]
        },
        "before_sensitive": false,
        "after_sensitive": {
          "records": [
            false
          ]
        }
      }
    },
```

Using a JMESPath query to identify potential source & target resources for `terraform state mv` operations, we identify matches based on the change dict matching:

```json
[
  {
    "source": "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.before.{name:name, records:records}}",
    "target": "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.after.{name:name, records:records}}",
  }
]
```

The JMESPath tranformation spec should result in a list of source & target dictionaries that have an address & change key, every source (i.e. resources that the current plan would destroy) is then compared against all of the resources the current plan would create, the comparison is a python dict equivalence. Matches are then recorded as a list of src/dst address pairs, and either reported or executed by `tf-tf`.

# Installation

Install via the internal Nexus PyPI group repo:

```
pip install --index-url https://nexus.taservs.net/repository/pypi-all/simple terraform-transform
```

# Development

TODO: Notes on using poetry

# Publishing to nexus.taservs.net

Configure nexus.taservs.net as a PyPI repository:

```bash
poetry config repositories.nexus https://nexus.taservs.net/repository/pypy-all/
```

Build & publish:

```bash
poetry build
poetry publish -r nexus
```

Install from nexus

```bash
pip install --index-url https://nexus.taservs.net/repository/pypi-all/simple terraform-transform
```
