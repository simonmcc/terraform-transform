import json
import logging
import os
import unittest

from tftf.transform import Transform

logger = logging.getLogger(__name__)


class Testtftf(unittest.TestCase):
    def test_transform_dict(self):
        transformations = [
            {
                "source": "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.before.{name:name, records:records}}",
                "target": "[?type == 'azurerm_private_dns_a_record'].{address: address, change: change.after.{name:name, records:records}}",
            }
        ]

        correctMove = {
            "src": 'azurerm_private_dns_a_record.legacy_vm["peu1ew1labd001"]',
            "dst": 'module.taservs_net["eu1.taservs.net"].azurerm_private_dns_a_record.legacy_vm["i-07f551c18b449b591"]',
        }

        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "dns-plan-pretty-labd.json"
        )
        with open(filename) as f:
            plan = json.load(f)
            moves = Transform(plan, transformations)

            self.assertIn(correctMove, moves)
