import json
import logging
import os
import unittest

import jmespath

from tftf import __version__

logger = logging.getLogger(__name__)


class Testtftf(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.1.0")

    def test_labd(self):
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "dns-plan-pretty-labd.json"
        )
        # jmespath query that returns a list of address, change tuples, used to match against
        # the resource_changes entities that match [?contains(change.actions, 'delete')]
        delete_filter = "[?contains(change.actions, 'delete')]"
        create_filter = "[?contains(change.actions, 'create')]"

        source = "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.before.{name:name, records:records}}"
        target = "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.after.{name:name, records:records}}"
        correctMove = {
            "src": 'azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"]',
            "dst": 'module.taservs_net["eu1.taservs.net"].azurerm_private_dns_a_record.legacy_vm["i-07f551c18b449b591"]',
        }

        with open(filename) as f:
            tf = json.load(f)

            resource_changes = tf["resource_changes"]
            deletes = jmespath.search(delete_filter, resource_changes)
            creates = jmespath.search(create_filter, resource_changes)

            resources_to_be_deleted = jmespath.search(source, deletes)
            resources_to_be_created = jmespath.search(target, creates)

            moves = []
            for r2delete in resources_to_be_deleted:
                for r2create in resources_to_be_created:
                    if r2create.get("change") == r2delete.get("change"):
                        moves.append(
                            {
                                "src": r2delete.get("address"),
                                "dst": r2create.get("address"),
                            }
                        )

            self.assertIn(correctMove, moves)


if __name__ == "__main__":
    unittest.main()
