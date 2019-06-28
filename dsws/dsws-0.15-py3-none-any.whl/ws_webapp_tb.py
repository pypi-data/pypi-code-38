"""
Workspace webapp for TensorBoard
KISS: Keep It Small & Simple

Start & Stop Tensorboard
"""

import os                                as _os
import time                              as _time
from IPython.core.display import HTML    as _HTML
from IPython.core.display import display as _display
import subprocess                        as _subprocess
import time                              as _time


from impala.dbapi import connect         as _connect
import pandas                            as _pd
from dsws.util import pretty             as _pretty
from dsws.util import sp                 as _sp
from dsws.util import standard_conn_qry  as _standard_conn_qry
from dsws.util import launch_url         as _launch_url 
from os import environ                   as _env
from ast import literal_eval             as _literal_eval


class Tb:

    def __init__(self):
        """
        TensorBoard is a webapp
        """
        self.conf=_literal_eval(_env[self.__module__.split(".")[-1].upper()])
        self.process=None

    def start(self, open_browser=False):
        if not self.process:
            self.process = _subprocess.Popen(self.conf['cmd'].split())
            _time.sleep(3)
        if open_browser:
          _launch_url(self.conf['url'])
        html = """
            <p><a href="{url}">Open Tensorboard</a></p>
          """.format(url=self.conf['url'])
        _display(_HTML(html))

    def stop(self):
        if self.process: 
          self.process.terminate()
          print "Tensorboard stopped."
          self.process = None
        else:
          print "Tensorboard is not running."

    def open_browser(self):
        self.start(open_browser=True)