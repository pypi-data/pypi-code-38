#!/usr/bin/python

import argparse
import sys
import prance
import json
import os
from . import expectation
from . import requester
from . import converter

def parse_yaml(filepath):
	exists = os.path.isfile(filepath)
	if not exists:
		print(filepath + ' does not exist')
	else:
		try:
			parser = prance.ResolvingParser(filepath)
			return parser.specification
		except:
			print(filepath + ' is not a valid contract file')
	return None

def mock(args):
	scenarios = []
	yaml = None
	expectations = None

	if args.s:
		scenarios = args.s

	if args.openapi_file:
		yaml = parse_yaml(args.openapi_file)

	if yaml:
		conv = converter.Converter();
		conv.set_scenarios(scenarios)
		conv.convert_opai(yaml);
		expectations = conv.expectations

	if args.mockserver_uri:
		mr = requester.MockserverRequester()
		mr.set_mockserver_uri(args.mockserver_uri)

		if expectations:
			mr.request_expectations(expectations)

def reset(args):
	if args.mockserver_uri:
		mr = requester.MockserverRequester()
		mr.set_mockserver_uri(args.mockserver_uri)
		mr.request_reset()

def arguments():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='title', dest='command')
	subparsers.required = True

	parser_mock = subparsers.add_parser('mock')
	parser_mock.set_defaults(func=mock)
	parser_mock.add_argument('mockserver_uri')
	parser_mock.add_argument('openapi_file')
	parser_mock.add_argument("-s", help="The scenarios to mock")

	parser_reset = subparsers.add_parser('reset')
	parser_reset.set_defaults(func=reset)
	parser_reset.add_argument('mockserver_uri')

	args = parser.parse_args()
	args.func(args)

def main():
	arguments()

if __name__ == '__main__':
	main()