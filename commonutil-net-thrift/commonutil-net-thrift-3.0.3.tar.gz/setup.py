#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup  # pylint: disable=import-error

setup(
		name="commonutil-net-thrift",
		version="3.0.3",  # REV-CONSTANT:rev 5d022db7d38f580a850cd995e26a6c2f
		description="Helper routine for Thrift",
		packages=[
				"commonutil_net_thrift",
				"commonutil_net_thrift.client",
				"commonutil_net_thrift.connector",
		],
		classifiers=[
				"Development Status :: 5 - Production/Stable",
				"Intended Audience :: Developers",
				"License :: OSI Approved :: MIT License",
				"Operating System :: POSIX",
				"Programming Language :: Python :: 3.7",
		],
		license="MIT License",
)

# vim: ts=4 sw=4 ai nowrap
