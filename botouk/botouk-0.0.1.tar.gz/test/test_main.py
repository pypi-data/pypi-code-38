# -*- coding: utf-8 -*-
import json
import os
import unittest
import warnings

import botouk as boto

warnings.filterwarnings("ignore", category=ResourceWarning,
                        message="unclosed.*<ssl.SSLSocket.*>")

conffile = os.path.join(os.path.dirname(__file__), './test_config.json')
with open(conffile) as f:
    CONFIG = json.load(f)


def remove_resource_warnings():
    warnings.filterwarnings("ignore", category=ResourceWarning,
                            message="unclosed.*<ssl.SSLSocket.*>")


class TestS3withSTS(unittest.TestCase):
    def setUp(self):
        remove_resource_warnings()

        self.config = CONFIG['s3']
        self.client = boto.S3.as_assume_role(
            self.config['aws_access_key_id'],
            self.config['aws_secret_access_key'],
            self.config['role_arn'],
        )

        print(self.client.__dict__)

    def test_download(self):
        res = self.client.download_file(
            bucket=self.config['download']['bucket'],
            key=self.config['download']['key'],
            filename=self.config['download']['filename'],
        )

        print(res)

    def test_list_objects(self):
        res = self.client.list_objects(
            bucket=self.config['download']['bucket']
        )

        print(res.files)


class TestSTS(unittest.TestCase):
    def setUp(self):
        remove_resource_warnings()

        self.config = CONFIG['sts']
        self.client = boto.STS.from_access_key(
            self.config['aws_access_key_id'],
            self.config['aws_secret_access_key'])

        print(self.client.__dict__)

    def test_assume_role(self):
        res = self.client.assume_role(
            role_arn=self.config['role_arn'],
        )
        print(res)
