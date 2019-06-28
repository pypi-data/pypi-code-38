import sys
from .run_shell import run_shell

def api_ls(args=[]):
  process = run_shell(['docker','stack','ls',args])
  if(process.returncode != 0):
      sys.exit(process.returncode)