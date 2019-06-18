# This is just a test runner for coverage
import os
from os.path import abspath, dirname

from commonconf.backends import use_configparser_backend

if __name__ == '__main__':
    path = abspath(os.path.join(dirname(__file__),
                                "..", "travis-ci", "test.conf"))
    use_configparser_backend(path, 'EMSAPI')

    from nose2 import discover
    discover()
