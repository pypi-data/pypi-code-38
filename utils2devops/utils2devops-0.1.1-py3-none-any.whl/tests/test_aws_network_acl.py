from unittest import TestCase, mock

import unittest

from utils2devops.aws.network_acl import list_network_acls
from utils2devops.tests.aws_base import SingletonSession

expected_result = """resource "aws_network_acl" "acl-f1780b98-network-acl-name" {
	vpc_id = "vpc-9e98f6f7"
	subnet_ids = ["subnet-a308c3ee","subnet-83a3dfea","subnet-345ce64f",]

	ingress {
		rule_no = "100"
		action = "allow"
		cidr_block = "0.0.0.0/0"
		ipv6_cidr_block = ""
		protocol = "6"
		from_port = 443
		to_port = 443
		icmp_code = 0
		icmp_type = 0
	}

	egress {
		rule_no = "100"
		action = "allow"
		cidr_block = "0.0.0.0/0"
		ipv6_cidr_block = ""
		protocol = "6"
		from_port = 80
		to_port = 80
		icmp_code = 0
		icmp_type = 0
	}

	tags {
		"Name" = "network-acl-name"
	}
}

"""
network_acls_elements_mock = {
    'NetworkAcls': [{
        'Associations': [{
            'NetworkAclAssociationId': 'aclassoc-8149f6e9',
            'NetworkAclId': 'acl-f1780b98',
            'SubnetId': 'subnet-a308c3ee'
        }, {
            'NetworkAclAssociationId': 'aclassoc-8f49f6e7',
            'NetworkAclId': 'acl-f1780b98',
            'SubnetId': 'subnet-83a3dfea'
        }, {
            'NetworkAclAssociationId': 'aclassoc-8049f6e8',
            'NetworkAclId': 'acl-f1780b98',
            'SubnetId': 'subnet-345ce64f'
        }],
        'Entries': [{
            'CidrBlock': '0.0.0.0/0',
            'Egress': True,
            'PortRange': {'From': 80, 'To': 80},
            'Protocol': '6',
            'RuleAction': 'allow',
            'RuleNumber': 100
        }, {
            'CidrBlock': '0.0.0.0/0',
            'Egress': True,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }, {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'PortRange': {'From': 443, 'To': 443},
            'Protocol': '6',
            'RuleAction': 'allow',
            'RuleNumber': 100
        }, {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }],
        'IsDefault': True,
        'NetworkAclId': 'acl-f1780b98',
        'Tags': [{
            'Key': 'Name',
            'Value': 'network-acl-name'
        }],
        'VpcId': 'vpc-9e98f6f7',
        'OwnerId': '397270606208'
    }],
    'ResponseMetadata': {
        'RequestId': 'e243f100-fda6-4623-b64f-21db69c5bf94',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'content-type': 'text/xml;charset=UTF-8',
            'content-length': '2937',
            'vary': 'accept-encoding',
            'date': 'Thu, 20 Jun 2019 17:20:52 GMT',
            'server': 'AmazonEC2'
        }, 'RetryAttempts': 0
    }
}


class AwsNetworkAclTestCase(TestCase):
    @mock.patch('boto3.Session', SingletonSession)
    def test_list_network_acls_nominal(self):
        # nominal
        profile_name = 'test'
        region_name = 'us-east-2'
        session = SingletonSession(profile_name=profile_name)
        client = session.client(service_name='ec2', region_name=region_name)
        client.network_acls_elements = network_acls_elements_mock
        ls = list_network_acls(profile_name, region_name)
        self.assertEqual(expected_result, str(ls[0]))


if __name__ == '__main__':
    unittest.main()
