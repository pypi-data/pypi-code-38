from ansible import errors
import os.path

def is_empty(arg):
  if arg is None or str(arg).strip() is '':
    return True
  return False

class FilterModule(object):
  '''Returns true if the argument is null or an empty string'''
  def filters(self):
      return {
          'is_empty' : is_empty
      }
