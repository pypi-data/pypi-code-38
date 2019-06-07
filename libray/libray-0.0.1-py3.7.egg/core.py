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

import os
import sys
import shutil
import requests
from bs4 import BeautifulSoup


try:
  from libray import iso
except ImportError:
  import iso

# Magic numbers / Constant variables

SECTOR = 2048
ALL_IRD_NET_LOC = 'http://jonnysp.bplaced.net/data.php'
GET_IRD_NET_LOC = 'http://jonnysp.bplaced.net/ird/'

# Utility functions

def to_int(data, order='big'):
  if isinstance(data, bytes):
    return int.from_bytes(data, order)


def to_bytes(data):
  if isinstance(data, str):
    return bytes(bytearray.fromhex(data))


ISO_SECRET = to_bytes("380bcf0b53455b3c7817ab4fa3ba90ed")
ISO_IV = to_bytes("69474772af6fdab342743aefaa186287")


def filesize(filename):
  return os.stat(filename).st_size


def read_seven_bit_encoded_int(fileobj, order):
  # Read out an Int32 7 bits at a time. The high bit
  # of the byte when on means to continue reading more bytes
  count = 0
  shift = 0
  byte = -1
  while (byte & 0x80) != 0 or byte == -1:
    # Check for a corrupted stream. Read a max of 5 bytes.
    if shift == (5 * 7):
      raise ValueError
    byte = to_int(fileobj.read(1), order)
    count |= (byte & 0x7F) << shift
    shift += 7
  return count


def error(msg):
  print('ERROR: %s' % msg)
  sys.exit(1)


def warning(msg):
  print('WARNING: %s. Continuing regardless' % msg)


def download_ird(ird_name):
  ird_link = GET_IRD_NET_LOC + ird_name
  r = requests.get(ird_link, stream=True)

  with open(ird_name, 'wb') as ird_file:
    r.raw.decode_content = True
    shutil.copyfileobj(r.raw, ird_file)


def ird_by_game_id(game_id):
  gameid = game_id.replace('-','')
  r = requests.get(ALL_IRD_NET_LOC, headers = {'User-Agent': 'Anonymous (You)' }, timeout=5)
  soup = BeautifulSoup(r.text, "html.parser")

  ird_name = False
  for elem in soup.find_all("a"):
    url = elem.get('href').split('/')[-1].replace('\\"','')
    if gameid in url:
      ird_name = url

  if not ird_name:
    error("Unable to download IRD, couldn't find link")  

  download_ird(ird_name)

  return(ird_name)
  

# Main functions


def decrypt(args):

  input_iso = iso.ISO(args)

  input_iso.decrypt(args)

  
  
