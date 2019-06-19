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
from flask import Flask, request, redirect
from optparse import OptionParser, Option
import logging
import logging.handlers


class Parser(OptionParser):
  """
  Parse all arguments.
  """
  def __init__(self, usage=None, version=None):
    """
    Initialize all options possibles.
    """
    OptionParser.__init__(self, usage=usage, version=version,
                          option_list=[
      Option("-l", "--log_file",
             help="The path of the log file",
             type=str,
             dest="log_file_path"),
    ])


  def check_args(self):
    """
    Check arguments
    """
    (options, args) = self.parse_args()
    if len(args) != 4:
      self.error("Incorrect number of arguments")
    host, port, upload_file, key = args

    upload_file = os.path.abspath(upload_file)

    return options, host, port, upload_file, key

class Config:
  def setConfig(self, option_dict, host, port, upload_file, key):
    """
    Set options given by parameters.
    """
    # Set options parameters
    for option, value in option_dict.__dict__.items():
      setattr(self, option, value)
    self.host = host
    self.port = int(port)
    self.upload_file = upload_file
    self.key = key

def run(config):
  """
  Will accept to upload a file only once. When a file has been uploaded,
  it will refuse any other upload.
  """
  app = Flask(__name__)

  if config.log_file_path is not None:
    file_handler = logging.handlers.RotatingFileHandler(
                config.log_file_path, maxBytes=500000, backupCount=5)

    file_handler.setLevel(logging.WARNING)

    app.logger.addHandler(file_handler)
    logging.getLogger('werkzeug').addHandler(file_handler)

  @app.route('/', methods=['GET', 'POST'])
  def upload_file():
    if os.path.exists(config.upload_file):
      template = app.open_resource('templates/done.html')
      return template.read()
    else:
      if request.method == 'POST':
        file = request.files['file']
        key = "%s" % request.form.get('key')
        if file and key:
          if key == config.key:
            file.save(config.upload_file)
            return redirect('/')
          else:
            # Bad key
            template = app.open_resource('templates/badkey.html')
            return template.read()
      template = app.open_resource('templates/index.html')
      return template.read()

  app.run(host=config.host, port=config.port)

def main():
  "Run default configuration."
  usage = "usage: onetimeupload [options] HOST PORT UPLOAD_FILE KEY"

  try:
    # Parse arguments
    config = Config()
    config.setConfig(*Parser(usage=usage).check_args())

    run(config)
    return_code = 0
  except SystemExit, err:
    # Catch exception raise by optparse
    return_code = err

  sys.exit(return_code)

