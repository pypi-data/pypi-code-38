import os
import re

class Dotenv():
  def __init__(self, file=""):
    self.dotenv = ""

  def load(self, file=""):
    if file == "":
      self.dotenv = os.path.dirname(os.path.abspath(__file__)) + "/.env"
    else:
      self.dotenv = file

    if os.path.exists(file):
      fh = open(file, "r")
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
