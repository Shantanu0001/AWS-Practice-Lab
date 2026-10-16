import json
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "stage3-network-egress.json"

class NetworkTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        cls.resources = cls.doc["Resources"]

    def test_required_parameters_exist(self):
        for name in ("VpcId", "PublicSubnetA", "PublicSubnetB", "AppSubnetA", "AppSubnetB"):
            self.assertIn(name, self.doc["Parameters"])

    def test_two_dedicated_route_tables_and_associations(self):
        self.assertEqual(self.resources["AppRouteTableA"]["Type"], "AWS::EC2::RouteTable")
        self.assertEqual(self.resources["AppRouteTableB"]["Type"], "AWS::EC2::RouteTable")
        self.assertEqual(self.resources["AppSubnetAssociationA"]["Type"], "AWS::EC2::SubnetRouteTableAssociation")
        self.assertEqual(self.resources["AppSubnetAssociationB"]["Type"], "AWS::EC2::SubnetRouteTableAssociation")
        self.assertEqual(self.resources["AppSubnetAssociationA"]["Properties"]["SubnetId"], {"Ref": "AppSubnetA"})
        self.assertEqual(self.resources["AppSubnetAssociationB"]["Properties"]["SubnetId"], {"Ref": "AppSubnetB"})

    def test_two_nat_gateways_and_eips(self):
        self.assertEqual(self.resources["NatGatewayA"]["Type"], "AWS::EC2::NatGateway")
        self.assertEqual(self.resources["NatGatewayB"]["Type"], "AWS::EC2::NatGateway")
        self.assertEqual(self.resources["NatEipA"]["Type"], "AWS::EC2::EIP")
        self.assertEqual(self.resources["NatEipB"]["Type"], "AWS::EC2::EIP")
        self.assertEqual(self.resources["NatGatewayA"]["Properties"]["SubnetId"], {"Ref": "PublicSubnetA"})
        self.assertEqual(self.resources["NatGatewayB"]["Properties"]["SubnetId"], {"Ref": "PublicSubnetB"})

    def test_same_az_routes_use_their_own_nat_and_route_table(self):
        a = self.resources["AppDefaultRouteA"]["Properties"]
        b = self.resources["AppDefaultRouteB"]["Properties"]
        self.assertEqual(a["DestinationCidrBlock"], "0.0.0.0/0")
        self.assertEqual(b["DestinationCidrBlock"], "0.0.0.0/0")
        self.assertEqual(a["RouteTableId"], {"Ref": "AppRouteTableA"})
        self.assertEqual(b["RouteTableId"], {"Ref": "AppRouteTableB"})
        self.assertEqual(a["NatGatewayId"], {"Ref": "NatGatewayA"})
        self.assertEqual(b["NatGatewayId"], {"Ref": "NatGatewayB"})

    def test_no_data_subnet_or_route_table_resources(self):
        serialized = json.dumps(self.resources)
        self.assertNotIn("DataSubnet", serialized)
        self.assertNotIn("DataRouteTable", serialized)


    def test_nat_gateways_use_their_distinct_eip_allocations(self):
        nat_a = self.resources["NatGatewayA"]["Properties"]
        nat_b = self.resources["NatGatewayB"]["Properties"]

        self.assertEqual(
            nat_a["AllocationId"],
            {"Fn::GetAtt": ["NatEipA", "AllocationId"]},
        )
        self.assertEqual(
            nat_b["AllocationId"],
            {"Fn::GetAtt": ["NatEipB", "AllocationId"]},
        )
        self.assertNotEqual(
            nat_a["AllocationId"],
            nat_b["AllocationId"],
        )

    def test_nat_gateways_do_not_depend_on_private_subnet_associations(self):
        self.assertNotIn("DependsOn", self.resources["NatGatewayA"])
        self.assertNotIn("DependsOn", self.resources["NatGatewayB"])

if __name__ == "__main__":
    unittest.main()
