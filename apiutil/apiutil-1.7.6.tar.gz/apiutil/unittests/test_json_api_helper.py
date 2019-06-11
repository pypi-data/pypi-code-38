# -*- coding: utf-8 -*-

import unittest

from apiutil.json_api import JsonApiPropertiesClass


class ApiResponse(JsonApiPropertiesClass):
    @property
    def m(self):
        return self.mandatory(u'a')

    @property
    def o(self):
        return self.optional(u'o')

    @property
    def od(self):
        return self.optional(u'od', u'default')


class TestJsonApiResponse(unittest.TestCase):

    def setUp(self):
        self.api_response = ApiResponse(response=u"""{"a": 1,
                                                      "o": 2}""")

    def tearDown(self):
        pass

    def test_mandatory(self):
        assert self.api_response.m == 1

    def test_optional(self):
        assert self.api_response.o == 2

    def test_optional_default(self):
        assert self.api_response.od == u"default"


if __name__ == u'__main__':
    unittest.main()
