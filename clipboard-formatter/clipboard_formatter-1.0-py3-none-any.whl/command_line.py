#!/usr/bin/env python
from .clipform import ClipboardSQLFormatter
from argparse import ArgumentParser

def main():

	clip = ClipboardSQLFormatter()
	clip.run_it()