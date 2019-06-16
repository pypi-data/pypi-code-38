#!/usr/bin/python

from neterraproxy import wsrv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("app_dir")
args = parser.parse_args()

username = getattr(args, "username")
password = getattr(args, "password")
app_dir = getattr(args,"app_dir")

wsrv.run(username, password, app_dir)