# from unittest import TestCase
# TODO
# from _pytest import unittest
#
# from utils2devops.aws.internet_gateway import list_internet_gateways
#
#
# class InternetGatewayTestCase(TestCase):
#
#     def test_list_internet_gateways_nominal(self):
#         # nominal
#         profile_name = 'terraform'
#         region_name = 'us-east-2'
#         ls = list_internet_gateways(profile_name, region_name)
#         self.assertEqual(ls, '__version__ = \'0.1.1\'')
#
#     def test_list_internet_gateways_bad_profile_name(self):
#         # fault bad profile_name
#         profile_name = 'terraform3'
#         region_name = 'us-east-2'
#         ls = list_internet_gateways(profile_name, region_name)
#         self.assertEqual(ls, 'No such file or directory')
#
#     def test_list_internet_gateways_bad_region_name(self):
#         # fault bad region_name
#         profile_name = 'terraform'
#         region_name = 'us-east-23'
#         ls = list_internet_gateways(profile_name, region_name)
#         self.assertEqual(ls, 'No such file or directory')
#
#
# if __name__ == '__main__':
#     unittest.main()
