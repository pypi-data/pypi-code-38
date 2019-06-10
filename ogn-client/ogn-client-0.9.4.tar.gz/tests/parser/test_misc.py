import unittest
import unittest.mock as mock
import os

from datetime import datetime
from time import sleep

from ogn.parser.parse import parse
from ogn.parser.exceptions import AprsParseError


class TestStringMethods(unittest.TestCase):
    @unittest.skip("Not yet implemented")
    def test_wtf(self):
        parse("BELG>OGNSDR,TCPIP*,qAC,GLIDERN2:/133835h4509.60NI00919.20E&/A=000246")


if __name__ == '__main__':
    unittest.main()
