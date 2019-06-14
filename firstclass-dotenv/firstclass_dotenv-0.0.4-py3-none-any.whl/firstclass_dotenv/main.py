import os
import re

class Dotenv():
  def __init__(self, file=""):
    if file:
      self.dotenv = file
    else:
      self.dotenv = ""

  def load(self, file=""):
    if file:
      self.dotenv = file
    else:
      if self.dotenv == "":
        self.dotenv = ".env"

    if os.path.exists(self.dotenv):
      with open(self.dotenv, "r") as fh:
        line = fh.readline()
        while line:
          line = line.strip()
          line = re.sub(r"\s*#.*", "", line)
          try:
            (key, val) = line.split("=")
            if val:
              val = re.sub('^"|"$', "", val)
              os.environ[key] = val
            else:
              os.environ[key] = ""
          except:
            line = fh.readline()
            next
          line = fh.readline()
