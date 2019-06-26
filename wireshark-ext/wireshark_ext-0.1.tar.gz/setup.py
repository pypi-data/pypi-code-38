#encoding:utf-8

from setuptools import setup, find_packages

kw = {
	"name":"wireshark_ext",
	"version": "0.1",
	"description": "Wireshark Format Tool",
	"long_description": "A tool for pretty format packet of Wireshark",
	"author":"yafeile",
	"author_email":"yafeile@sohu.com",
	"url":"https://github.com/yafeile/wireshark_ext",
	"extras_require":{
	   "six":["six>=1.12.0"]
	},
	"packages": find_packages(),
}
setup(**kw)