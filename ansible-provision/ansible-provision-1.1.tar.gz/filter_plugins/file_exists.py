from ansible import errors
import os.path

def file_exists(file):
    return os.path.isfile(file)

def dir_exists(file):
    return os.path.isdir(file)

class FilterModule(object):
    '''Returns true if the file exists'''
    def filters(self):
        return {
            'file_exists' : file_exists,
            'dir_exists': dir_exists
        }
