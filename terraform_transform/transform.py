import logging

import jmespath

logger = logging.getLogger(__name__)


class Transform:

    delete_filter = "[?contains(change.actions, 'delete')]"
    create_filter = "[?contains(change.actions, 'create')]"

    def __init__(self, plan, transformations):
        """
        plan - dict representing terraform plan in json format
        transformations - list of dicts describe the required transformations:
        [ { 'source': "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.before.{name:name, records:records}}",
            'target': "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.after.{name:name, records:records}}" } ]


        returned object is an iterable list of dicts with source/target addresses, suitable for executing with `terraform state mv $src $target
        """

        self._moves = []

        resource_changes = plan["resource_changes"]
        deletes = jmespath.search(Transform.delete_filter, resource_changes)
        creates = jmespath.search(Transform.create_filter, resource_changes)

        for t in transformations:

            resources_to_be_deleted = jmespath.search(t.get("source"), deletes)
            resources_to_be_created = jmespath.search(t.get("target"), creates)

            for r2delete in resources_to_be_deleted:
                for r2create in resources_to_be_created:
                    if r2create.get("change") == r2delete.get("change"):
                        self._moves.append(
                            {
                                "src": r2delete.get("address"),
                                "dst": r2create.get("address"),
                            }
                        )

    def __iter__(self):
        for m in self._moves:
            yield m
