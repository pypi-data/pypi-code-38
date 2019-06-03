__version__ = '0.1.9'

import os
import re

import numpy as np

# Tank event types (tsqEventHeader.type)
EVTYPE_UNKNOWN  = int('00000000', 16)
EVTYPE_STRON    = int('00000101', 16)
EVTYPE_STROFF	= int('00000102', 16)
EVTYPE_SCALAR	= int('00000201', 16)
EVTYPE_STREAM	= int('00008101', 16)
EVTYPE_SNIP		= int('00008201', 16)
EVTYPE_MARK		= int('00008801', 16)
EVTYPE_HASDATA	= int('00008000', 16)
EVTYPE_UCF		= int('00000010', 16)
EVTYPE_PHANTOM	= int('00000020', 16)
EVTYPE_MASK		= int('0000FF0F', 16)
EVTYPE_INVALID_MASK	= int('FFFF0000', 16)

EVMARK_STARTBLOCK	= int('0001', 16)
EVMARK_STOPBLOCK	= int('0002', 16)

DFORM_FLOAT		 = 0
DFORM_LONG		 = 1
DFORM_SHORT		 = 2
DFORM_BYTE		 = 3
DFORM_DOUBLE	 = 4
DFORM_QWORD		 = 5
DFORM_TYPE_COUNT = 6

ALLOWED_FORMATS = [np.float32, np.int32, np.int16, np.int8, np.float64, np.int64]
ALLOWED_EVTYPES = ['all','epocs','snips','streams','scalars']

MASKS = {1:0x01, 2:0x03, 4:0x0f, 8:0xff}

def get_files(dir, ext):
    result = []
    for file in os.listdir(dir):
        if file.endswith(ext):
            result.append(os.path.join(dir, file))
    return result

def fix_var_name(var_str, verbose=False):
    if not var_str[0].isalnum():
        var_str = 'x' + var_str
    fixed_name = re.sub('\W|^(?=\d)','_', var_str)
    if fixed_name != var_str and verbose:
        print('info: {0} is not a valid Python variable name, changing to {1}'.format(var_str, fixed_name))
    return fixed_name

class StructType(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        
    def __repr__(self):
        if len(self.__dict__.items()) < 1:
            return '{}'

        parts = []
        for k in self.__dict__.keys():
            if isinstance(self.__dict__[k], StructType):
                rrr = repr(self.__dict__[k])
                parts.append(k + "\t[struct]")
            else:
                parts.append(k + ":\t" + repr(self.__dict__[k]))
        result = '\n'.join(parts)
        return result
    
    def __bool__(self):
        return len(self.__dict__.keys()) > 0
    
    def __getitem__(self, key):
        val = getattr(self, key)
        return val
    
    def __setitem__(self, key, val):
        return setattr(self, key, val)
    
    def keys(self):
        return self.__dict__.keys()
    
    def items(self):
        return self.__dict__.items()
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

# converts incoming packet into sort code counts
def unpack(data, sort_codes=2, bits_per_bin=4):
    mask = MASKS[bits_per_bin]
    return [np.bitwise_and(data >> bits_per_bin * x, mask) for x in range(sort_codes)]

def download_demo_data():
    import os
    if not os.path.exists('data.zip'):
        import urllib.request
        import sys
        import time

        url = 'https://www.tdt.com/files/examples/TDTExampleData.zip'
        print('downloading demo data...')

        def reporthook(count, block_size, total_size):
            global start_time
            if count == 0:
                start_time = time.time()
                return
            duration = time.time() - start_time
            progress_size = int(count * block_size)
            if duration > 0:
                speed = int(progress_size / (1024 * duration))
                percent = min(int(count * block_size * 100 / total_size), 100)
                sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds elapsed" %
                                (percent, progress_size / (1024 * 1024), speed, duration))
                sys.stdout.flush()

        urllib.request.urlretrieve(url, 'data.zip', reporthook)
        print()

    if not os.path.exists('data'):
        try:
            print('unzipping demo data...')
            import zipfile
            zip_ref = zipfile.ZipFile('data.zip', 'r')
            zip_ref.extractall('data')
            zip_ref.close()
        except:
            print('problem with zip, downloading again')
            os.remove('data.zip')
            return download_demo_data()

    print('demo data ready')

from .TDTbin2py import read_block, read_sev
from .TDTfilter import epoc_filter
from .SynapseAPI import SynapseAPI
from .TDTUDP import TDTUDP