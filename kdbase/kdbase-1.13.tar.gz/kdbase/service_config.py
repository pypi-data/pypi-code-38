#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from optparse import OptionParser
from singleton import *
import os
import time
import sys

optParser = OptionParser()
optParser.add_option("-p", "--project", type="string", dest="project", help='')
optParser.add_option("-e", "--env", type="string", dest="env", help='')


@singleton
class __ServiceManager():
    def __init__(self):
        self.conf_file = './service_conf.ini' 
        self.load()

    def load(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(self.conf_file)
        self.mtime = os.path.getmtime(self.conf_file)
        sys.stderr.write('load conf file at [%s]\n' % time.ctime(time.time()))

    def reload(self):
        if self.mtime != os.path.getmtime(self.conf_file):
            self.load()

    def get_ex(self, name, key, dft_val):
        self.reload()
        try:
            return self.cf.get(name, key)
        except Exception, e:
            print e
            return dft_val

    def get(self, name, key):
        self.reload()
        return self.cf.get(name, key)

    def has(self, name, key):
        return self.cf.has_option(name, key)


def GET_CONF_EX(name, key, dft_val):
    manager = __ServiceManager()
    return manager.get_ex(name, key, dft_val)


def GET_CONF(name, key):
    manager = __ServiceManager()
    return manager.get(name, key)


def HAS_CONF(name, key):
    manager = __ServiceManager()
    return manager.has(name, key)


def SET_CONF_FILE(conf_file):
    manager = __ServiceManager()
    manager.conf_file = conf_file 
    manager.load()


def main():
    print GET_CONF('hadoop', 'user_name')
    print GET_CONF('sentinel', 'hosts')


if __name__ == '__main__':
    main()
