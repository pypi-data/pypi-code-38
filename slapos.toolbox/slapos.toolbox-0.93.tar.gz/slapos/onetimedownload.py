##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os
import sys
from optparse import OptionParser, Option
import urllib


class Parser(OptionParser):
  """
  Parse all arguments.
  """

  def check_args(self):
    """
    Check arguments
    """
    (options, args) = self.parse_args()
    if len(args) != 2:
      self.error("Incorrect number of arguments")
    url, file_path = args

    return url, file_path

class Config:
  def setConfig(self, url, file_path):
    """
    Set options given by parameters.
    """
    self.url = url
    self.file_path = file_path

def onetimedownload(url, file_path):
  url_file = urllib.urlopen(url)
  data = url_file.read()
  file_object = open(file_path, 'w')
  file_object.write(data)
  file_object.close()

def main():
  "Run default configuration."
  usage = "usage: onetimedownload URL FILE_PATH"

  try:
    # Parse arguments
    config = Config()
    config.setConfig(*Parser(usage=usage).check_args())

    onetimedownload(config.url, config.file_path)
    return_code = 0
  except SystemExit, err:
    # Catch exception raise by optparse
    return_code = err

  sys.exit(return_code)

