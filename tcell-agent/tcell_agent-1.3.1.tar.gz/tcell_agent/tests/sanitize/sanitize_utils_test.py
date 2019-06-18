# coding=utf-8

import unittest

from tcell_agent.sanitize.sanitize_utils import java_hash, strip_uri, \
     hmac_half
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext


class SanitizerUtilsTest(unittest.TestCase):
    def test_strip_uri(self):
        self.assertEqual(strip_uri("/abc/def?bbb=abcd"), "/abc/def?bbb=")
        self.assertEqual(strip_uri("https://aaa:8000/abc/def?bbb=ccbc"), "https://aaa:8000/abc/def?bbb=")
        self.assertEqual(strip_uri("https://aaa:8000/abc/def?b=b&b=b"), "https://aaa:8000/abc/def?b=&b=")
        self.assertEqual(strip_uri("https://aaa:8000/abc/def?b=h&a=h&c"), "https://aaa:8000/abc/def?b=&a=&c=")

    def test_strip_query_string(self):
        self.assertEqual(strip_uri("/abc/def?%C2%B5=%C3%A9%3Cscript%3E%C2%B5"), "/abc/def?%C2%B5=")
        self.assertEqual(
            strip_uri("http://192.168.99.100:3000/account/signup/?%C2%B5=%C3%A9%3Cscript%3E%C2%B5"),
            "http://192.168.99.100:3000/account/signup/?%C2%B5=")

    def test_strip_path_string(self):
        self.assertEqual(
            strip_uri("/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=ccbc"),
            "/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=")
        self.assertEqual(
            strip_uri("http://192.168.99.100:3000/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=ccbc"),
            "http://192.168.99.100:3000/vulnerabilities/%C2%B5%3Cscript%3E/?bbb=")

    def test_utf8_chars_java_hash(self):
        self.assertEqual(java_hash("normal"), -1039745817)
        self.assertEqual(java_hash(u"müller"), -938338084)
        self.assertEqual(java_hash(u"émail"), 218524192)

    def test_hmac_half_with_hmac_key(self):
        config = ConfigurationBuilder().update_attribute(
            "hmac_key", "hmac-key"
        ).update_attribute(
            "api-key", None
        ).build()
        with ConfigContext(config):
            self.assertEqual(hmac_half("session-id"), "ee7e5694d32aedcf895b012d6dcec17d")

    def test_hmac_half_with_api_key(self):
        config = ConfigurationBuilder().update_attribute(
            "hmac_key", None
        ).update_attribute(
            "api-key", "api-key"
        ).build()
        with ConfigContext(config):
            self.assertEqual(hmac_half("session-id"), "ab7074d0bf86c2884766d88b6ad9de4a")
