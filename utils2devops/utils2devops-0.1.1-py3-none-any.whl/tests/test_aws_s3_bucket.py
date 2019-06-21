import datetime
from dateutil.tz import tzutc
import unittest
from unittest import TestCase, mock

from utils2devops.aws.s3_bucket import list_s3_bucket
from utils2devops.tests.aws_base import SingletonSession, SingletonResource
from utils2devops.tools.string import strip_space_tab

s3_bucket_data_mock = {
    'ResponseMetadata': {
        'RequestId': '5D79E1D7FD99C6DD',
        'HostId': 'nwnM94qNS3evcPVy6pECIcKBjrq18X5rPS+V90bsDYcMI+rGGm2iwd2Lbl0I9J21hND2g1GJV64=',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'x-amz-id-2': 'nwnM94qNS3evcPVy6pECIcKBjrq18X5rPS+V90bsDYcMI+rGGm2iwd2Lbl0I9J21hND2g1GJV64=',
            'x-amz-request-id': '5D79E1D7FD99C6DD',
            'date': 'Wed, 19 Jun 2019 22:30:05 GMT',
            'content-type': 'application/xml',
            'transfer-encoding': 'chunked',
            'server': 'AmazonS3'
        },
        'RetryAttempts': 0
    },
    'Buckets': [
        {
            'Name': 'hf-in',
            'CreationDate': datetime.datetime(2019, 6, 19, 22, 29, 24, tzinfo=tzutc())
        },
        {
            'Name': 'hf-out',
            'CreationDate': datetime.datetime(2019, 6, 19, 22, 29, 50, tzinfo=tzutc())
        }
    ],
    'Owner': {
        'ID': 'a99ad60ae4ed2de14bb0869c1f1700e8bdafbe380d587499d614104740a85ba8'
    }
}

s3_list_expected = strip_space_tab("""resource "aws_s3_bucket" "hf-in" {
    bucket = "hf-in"
    acl = "private"
    versioning {
        enabled = false
    }
}

resource "aws_s3_bucket" "hf-out" {
    bucket = "hf-out"
    acl = "private"
    versioning {
        enabled = false
    }
}

""")


class AwsS3BucketTestCase(TestCase):
    @mock.patch('boto3.resource', SingletonResource)
    @mock.patch('boto3.Session', SingletonSession)
    def test_list_s3_bucket_nominal(self):
        # nominal
        profile_name = 'test'
        region_name = 'us-east-2'
        session = SingletonSession(profile_name=profile_name)
        client = session.client(service_name='s3', region_name=region_name)
        client.s3_bucket_data = s3_bucket_data_mock
        ls = list_s3_bucket(profile_name, region_name)
        prepare = strip_space_tab(str(ls[0]) + str(ls[1]))
        self.assertEqual(s3_list_expected, prepare)

    # @mock.patch('boto3.Session', SingletonSession)
    # def test_list_lambda_bad_profile_name(self):
    #     # fault bad profile_name
    #     profile_name = 'terraform3'
    #     region_name = 'us-east-2'
    #     ls = list_api_gateway(profile_name, region_name)
    #     self.assertEqual(ls, 'No such file or directory')
    #
    # @mock.patch('boto3.Session', SingletonSession)
    # def test_list_lambda_bad_region_name(self):
    #     # fault bad region_name
    #     profile_name = 'terraform'
    #     region_name = 'us-east-23'
    #     ls = list_api_gateway(profile_name, region_name)
    #     self.assertEqual(ls, 'No such file or directory')


if __name__ == '__main__':
    unittest.main()
