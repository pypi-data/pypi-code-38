# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from kengste.hello.greet.greet import greet


if __name__ == '__main__':
  greetees = sys.argv[1:] or ['world']
  for greetee in greetees:
    print(greet(greetee))


class Class2:

  def show():
    multi_line_string = """This is the first line.
    Class 1.
    and this is the second line
    and this is the third line"""
    print(multi_line_string)

def show3():
  multi_line_string = """This is the first line.
  Class 1.
  and this is the second line
  and this is the third line"""
  print(multi_line_string)
