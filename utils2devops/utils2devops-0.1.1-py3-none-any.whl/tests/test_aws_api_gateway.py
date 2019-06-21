# from unittest import TestCase
# TODO
# from _pytest import unittest
#
# from utils2devops.aws.api_gateway_v2 import list_api_gateway
#
# TODO
# class AwsApiGatewayTestCase(TestCase):
#
#     def test_list_api_gateways_nominal(self):
#         # nominal
#         profile_name = 'terraform'
#         region_name = 'us-east-2'
#         ls = list_api_gateway(profile_name, region_name)
#         self.assertEqual(ls, '__version__ = \'0.1.1\'')
#
#     def test_list_internet_gateways_bad_profile_name(self):
#         # fault bad profile_name
#         profile_name = 'terraform3'
#         region_name = 'us-east-2'
#         ls = list_api_gateway(profile_name, region_name)
#         self.assertEqual(ls, 'No such file or directory')
#
#     def test_list_internet_gateways_bad_region_name(self):
#         # fault bad region_name
#         profile_name = 'terraform'
#         region_name = 'us-east-23'
#         ls = list_api_gateway(profile_name, region_name)
#         self.assertEqual(ls, 'No such file or directory')
#
#
# if __name__ == '__main__':
#     unittest.main()
