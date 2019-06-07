#!/usr/bin/env python3
# -*- coding: utf8 -*-

# libray - Libre Blu-Ray PS3 ISO Tool
# Copyright (C) 2018 Nichlas Severinsen
#
# This file is part of libray.
#
# libray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libray.  If not, see <https://www.gnu.org/licenses/>.


import argparse


try:
  from libray import core
except ImportError:
  import core


if __name__ == '__main__':

  # Parse command line arguments with argpase
  parser = argparse.ArgumentParser(description='A Libre (FLOSS) Python application for unencrypting, extracting, repackaging, and encrypting PS3 ISOs')
  parser.add_argument('-v', '--verbose', help="Increase verbosity", action='count')
  parser.add_argument('-o', '--output', dest='output', type=str, help="Output filename", default='output.iso')
  parser.add_argument('-k', '--ird', dest='ird', type=str, help="Path to .ird file", default="")
  required = parser.add_argument_group('required arguments')
  required.add_argument('-i', '--iso', dest='iso', type=str, help="Path to .iso file", required=True)
  args = parser.parse_args()

  core.decrypt(args)

