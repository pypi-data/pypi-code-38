import requests
import re
import gzip
import os
from datetime import datetime
import time
import sys

#to disable warnings related to https certificates verification
import urllib3
urllib3.disable_warnings()

import logging
logger = logging.getLogger("downloadepg.py")

class EPGDownloader:
    def __init__(self, script_dir):
        logging.info("EPG downloader initialised: {0}".format(str(datetime.now())))
        self.script_dir = script_dir
        self.url = "http://epg.kodibg.org/dl.php"
        self.filename = "epg"

    def __donwload(self):
        try:
            logging.info("download started: {0}".format(str(datetime.now())))
            r = requests.get(self.url, allow_redirects=True)
            with open(self.script_dir + "/" + self.filename + ".xml.gz", "w") as f:
                f.write(r.content)
                f.close()
        except requests.exceptions.RequestException as err:
            print(err("message"))
            sys.exit(1)

    def extract(self):
        self.__donwload()
        f = gzip.open(self.script_dir + "/" + self.filename + ".xml.gz", 'rb')
        file_content = f.read()
        f.close()
        with open(self.script_dir + "/" + self.filename + ".xml", "w") as f:
            f.write(file_content)
            f.close()

if __name__ == "__main__":
    print ("go go go")
    d = EPGDownloader()
    print (d.script_dir)
    d.extract()
