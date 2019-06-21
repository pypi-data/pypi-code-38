#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Gunther <siebenkopf@googlemail.com>
# @date: Tue Dec 29 09:23:53 MST 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.



def main():

  import pkg_resources
  import sys
  import os
  if sys.version_info[0] <= 2:
    import urllib2 as urllib
  else:
    import urllib.request as urllib
  import tarfile
  import argparse
  parser = argparse.ArgumentParser(description='Download and extract the Voxforge database.')
  parser.add_argument("--address", default="VOXFORGE_DATABASE", help="Where downloaded archives will be placed. Default is 'VOXFORGE_DATABASE' folder.")
  args = parser.parse_args()

  

  directory = args.address
  if not os.path.exists(directory):
    print ("Creating intermediate directory '%s', where downloaded archives will be placed" % directory)
    os.makedirs(directory)

  baselink = "http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit"
  listfile = pkg_resources.resource_filename("bob.db.voxforge", "lists/list_of_tgz_files.lst")


  with open(listfile) as lf:
    for line in lf:
      line = line.strip()
      basename = os.path.splitext(line)[0]
      outfile = os.path.join(directory, basename)
      if os.path.exists(outfile):
        print ("Skipping existing entry '%s'" % outfile)
        continue

      url = baselink + "/" + line
      tempfile = os.path.join(directory, line)
      try:
        print ("Downloading file '%s' to '%s'" % (url, tempfile))
        url = urllib.urlopen(url)
        dfile = open(tempfile, 'wb')
        dfile.write(url.read())
        dfile.close()

        print ("Extracting file '%s' to '%s'" % (tempfile, outfile))
        tar = tarfile.open(tempfile, 'r')
        tar.extractall(directory)
        tar.close()

      except Exception as e:
        print ("ERROR: Downloading and unpacking of '%s' was not successful: %s" % (tempfile, e))
        # TODO: should we just try to re-download, or leave it to the user to call this script again?

      finally:
        # TODO: should we leave possibly broken files here, so that it can be inspected later?
        os.remove(tempfile)

