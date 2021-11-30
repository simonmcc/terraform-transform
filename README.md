#!/usr/bin/env python3
#
 Generate terraform state mv steps reduce delete/recreate churn


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
