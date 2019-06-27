#encoding:utf-8

from setuptools import setup, find_packages

kw = {
	"name":"har",
	"version": "0.1",
	"description": "Har parser Tool",
	"long_description": "A tool for parser the http archive file",
	"author":"yafeile",
	"author_email":"yafeile@sohu.com",
	"url":"https://github.com/yafeile/harparser",
	"packages": find_packages(),
}
setup(**kw)