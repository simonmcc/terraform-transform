# tftf - Terraform Transforms

This tool will parse a Terraform plan file and mv resources that would normally be deleted & re-created.

Arbitrary delete/re-create cycles can be prevented by moving the resourecs to their new address in terraform state, avoiding the delete/recreate.

Potential source & target addresses are identified by JMESPath queries applied to the [Terraform Plan
Representation](https://www.terraform.io/docs/internals/json-format.html#plan-representation)

There's a `local_file` example in [examples/terraform](examples/terraform), and a wrapper `Makefile` use to simulate avoiding a destroy/create cycle by manipulating the terraform state.


Inspired by

* https://github.com/bcochofel/terraplanfeed
* https://github.com/aleksanderaleksic/tgmigrate
* https://github.com/minamijoyo/tfmigrate



## Detailed real-world example

Given:
```hcl
 azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"] will be destgrbhhuvdvknibrvtegdldguberiiektcdnil
 royed
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

```
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

 Generate: terraform state mv azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"] module.taservs_net["eu1.taservs.net"].azurerm_private_dns_a_record.legacy_vm["i-07f551c18b449b591"]

 In the json output format, the resource_changes list has entries like this:

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

  Given that the resource to be deleted came from a static list, we don't have a direct mapping to match against the generated names (i-07f551c18b449b591)
