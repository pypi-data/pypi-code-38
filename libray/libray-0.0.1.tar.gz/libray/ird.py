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
import zlib
import shutil


try:
  from libray import core
except ImportError:
  import core


class IRD:
  """Class for handling .ird files

  Attributes:
    version: IRD version number
    game_id: PS3 game identifier
    game_name: Name of PS3 game
    update_version: PS3 firmware update version
    game_version: PS3 game version
    app_version: PS3 app version
    region_count: How many encrypted regions are in the .iso
    file_count: How many files are supposed to be in the .iso
    data1: Encryption key
  """

  ORDER = 'little'
  TEMP_FILE = 'ird'
  MAGIC_STRING = b"3IRD"


  def __init__(self, args):
    """IRD constructor using args from argparse"""

    self.uncompress(args.ird) # TODO: Try/Except?

    self.size = core.filesize(self.TEMP_FILE)
    with open(self.TEMP_FILE, 'rb') as input_ird:
      if input_ird.read(4) != self.MAGIC_STRING:
        core.error("Either not an IRD file, corruped IRD file, or unknown IRD format")

      self.version = core.to_int(input_ird.read(1), self.ORDER)
      self.game_id = input_ird.read(9)
      name_length = core.read_seven_bit_encoded_int(input_ird, self.ORDER)
      self.game_name = input_ird.read(name_length).decode('utf8')
      self.update_version = input_ird.read(4)
      self.game_version = input_ird.read(5)
      self.app_version = input_ird.read(5)

      if self.version == 7:
        self.identifier = input_ird.read(4)

      header_length = (core.to_int(input_ird.read(4), self.ORDER))
      self.header = input_ird.read(header_length)
      footer_length = (core.to_int(input_ird.read(4), self.ORDER))
      self.footer = input_ird.read(footer_length)

      self.region_count = core.to_int(input_ird.read(1), self.ORDER)
      self.region_hashes = []
      for i in range(0, self.region_count):
        self.region_hashes.append(input_ird.read(16))

      self.file_count = core.to_int(input_ird.read(4), self.ORDER)
      self.file_hashes = []
      for i in range(0, self.file_count):
        key = core.to_int(input_ird.read(8), self.ORDER)
        val = input_ird.read(16)
        self.file_hashes.append({'key': key, 'val': val})

      if self.version >= 9:
        self.pic = input_ird.read(115)

      unused_bytes = input_ird.read(4) # Yeah, I don't know either.

      self.data1 = input_ird.read(16)
      self.data2 = input_ird.read(16)

      if self.version < 9:
        self.pic = input_ird.read(115)

      if self.version < 7:
        self.uid = core.to_int(input_ird.read(4), self.ORDER)

      if args.verbose:
        self.print_info()

    os.remove(self.TEMP_FILE)


  def uncompress(self, filename):
    """Uncompress IRD. Assumes given .ird file is not compressed, but then tries to decompress it with zlib/gzfile if it was not uncompressed"""

    uncompress = False
    with open(filename, 'rb') as input_ird:
      if input_ird.read(4) != self.MAGIC_STRING:
        uncompress = True

    if uncompress:
      with open(filename, 'rb') as gzfile:
        with open(self.TEMP_FILE, 'wb') as tmpfile:
          tmpfile.write(zlib.decompress(gzfile.read(), zlib.MAX_WBITS|16))
    else:
      shutil.copyfile(filename, self.TEMP_FILE)


  def print_info(self):
    # TODO: This could probably have been a __str__? Who cares?
    """Print some info about the IRD"""

    print('Info from IRD:')
    print('Version: %s' % self.version)
    print('Game ID: %s' % self.game_id)
    print('Game Name: %s' % self.game_name)
    print('Update Version: %s' % self.update_version)
    print('Game Version: %s' % self.game_version)
    print('App Version: %s' % self.app_version)
    print('Region Count: %s' % self.region_count)
    print('File Count: %s' % self.file_count)
    print('Data1: %s' % self.data1.hex())
    print('Data2: %s' % self.data2.hex())


