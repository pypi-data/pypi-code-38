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


import sys
from tqdm import tqdm
from Crypto.Cipher import AES

try:
  from libray import core
  from libray import ird
except ImportError:
  import core
  import ird


class ISO:

  
  NUM_INFO_BYTES = 4


  def __init__(self, args):
    with open(args.iso, 'rb') as input_iso:
      self.size = core.filesize(args.iso)
      self.number_of_regions = core.to_int(input_iso.read(self.NUM_INFO_BYTES))
      unused_bytes = input_iso.read(self.NUM_INFO_BYTES) # Yeah, I don't know either.

      self.regions = self.read_regions(input_iso, args.iso)

      input_iso.seek(core.SECTOR)
      playstation = input_iso.read(16)
      self.game_id = input_iso.read(16).decode('utf8').strip()

    if args.verbose:
      self.print_info()

    if not args.ird:
      core.warning('No IRD file specified, downloading required file')
      args.ird = core.ird_by_game_id(self.game_id) # Download ird

    self.ird = ird.IRD(args)

    if self.ird.region_count != len(self.regions)-1:
      core.error('Corrupt ISO. Expected %s regions, found %s regions' % (self.ird.region_count, len(self.regions)-1))

    if self.regions[-1]['start'] > self.size:
      core.error('Corrupt ISO. Expected filesize larger than %.2f GiB, actual size is %.2f GiB' % (self.regions[-1]['start'] / 1024**3, self.size / 1024**3 ) )

    cipher = AES.new(core.ISO_SECRET, AES.MODE_CBC, core.ISO_IV)
    self.disc_key = cipher.encrypt(self.ird.data1)


  def decrypt(self, args):

    print('Decrypting with disc key: %s' % self.disc_key.hex())

    with open(args.iso, 'rb') as input_iso:
      with open(args.output, 'wb') as output_iso:

        pbar = tqdm(total= (self.size // 2048) - 4 )
      
        for i, region in enumerate(self.regions):
          input_iso.seek(region['start'])

          if not region['enc']:
            while input_iso.tell() < region['end']:
              data = input_iso.read(core.SECTOR)
              if not data:
                core.warning("Trying to read past the end of the file")
                break
              pbar.update(1)
              output_iso.write(data)
            continue
          else:
            while input_iso.tell() < region['end']:
              num = input_iso.tell() // 2048
              iv = bytearray([0 for i in range(0,16)])
              for j in range(0,16):
                iv[16 - j - 1] = (num & 0xFF)
                num >>= 8
            
              data = input_iso.read(core.SECTOR)
              if not data:
                core.warning("Trying to read past the end of the file")
                break
              pbar.update(1)
             
              cipher = AES.new(self.disc_key, AES.MODE_CBC, bytes(iv))
              decrypted = cipher.decrypt(data)
            
              output_iso.write(decrypted)
              
          pbar.close()

  def read_regions(self, input_iso, filename):
    regions = []
    
    encrypted = False
    for i in range(0, self.number_of_regions*2):
      regions.append({
        'start': core.to_int(input_iso.read(self.NUM_INFO_BYTES))*core.SECTOR, 
        'end': core.to_int(input_iso.read(self.NUM_INFO_BYTES))*core.SECTOR, 
        'enc': encrypted
      })
      input_iso.seek(input_iso.tell() - self.NUM_INFO_BYTES)
      encrypted = not encrypted
    regions[-1]['end'] = self.size

    return regions


  def print_info(self):
    print('Info from ISO:')
    print('Regions: %s (%s)' % (self.number_of_regions, self.number_of_regions*2) )
    for i, region in enumerate(self.regions):
      print(i, region)

    