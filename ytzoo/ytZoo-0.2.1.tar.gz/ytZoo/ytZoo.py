from __future__ import print_function
import pickle
import time
import os

import logging
from logging import handlers
import sys


def cprint(*args, **kwargs):
    """Markup words wrapped in << and >> and print them out.
    
    Parameters
    =========
    b : bool, default True
        Use bold font.
    c : str, default 'yellow'
        Color of the font.
    h : bool, default Flase
        Highlight the font.
    """
    b = kwargs.pop('b', True)
    c = kwargs.pop('c', 'yellow')
    h = kwargs.pop('h', False)
    color2num = dict(
        gray=30,
        red=31,
        green=32,
        yellow=33,
        blue=34,
        magenta=35,
        cyan=36,
        white=37,
        crimson=38
    )
    # Import six here so that `utils` has no import-time dependencies.
    # We want this since we use `utils` during our import-time sanity checks
    # that verify that our dependencies (including six) are actually present.
    import six
    attr = []
    num = color2num[c]
    if h:
        num += 10
    attr.append(six.u(str(num)))
    if b:
        attr.append(six.u('1'))
    attrs = six.u(';').join(attr)
    prefix = six.u('\x1b[%sm' % attrs)
    suffix = six.u('\x1b[0m')

    s = args[0]
    s = s.replace('<<', prefix)
    s = s.replace('>>', suffix)
    args = (s, *args[1:])

    return print(*args, **kwargs)

# from OpenAi.gym
def colorize(string, color, bold=False, highlight=False):
    """Return string surrounded by appropriate terminal color codes to
    print colorized text. Valid colors: gray, red, green, yellow,
    blue, magenta, cyan, white, crimson
    """
    color2num = dict(
        gray=30,
        red=31,
        green=32,
        yellow=33,
        blue=34,
        magenta=35,
        cyan=36,
        white=37,
        crimson=38
    )
    # Import six here so that `utils` has no import-time dependencies.
    # We want this since we use `utils` during our import-time sanity checks
    # that verify that our dependencies (including six) are actually present.
    import six
    attr = []
    num = color2num[color]
    if highlight: num += 10
    attr.append(six.u(str(num)))
    if bold: attr.append(six.u('1'))
    attrs = six.u(';').join(attr)
    return six.u('\x1b[%sm%s\x1b[0m') % (attrs, string)

from pathlib import Path
class FileIO():
    @staticmethod
    def glob(pattern):
        '''Get a list of files that satisfy the given pattern. '''
        from glob import glob
        return glob(pattern, recursive=True)
    @staticmethod
    def exists(path):
        return Path(path).exists()
    @staticmethod
    def is_dir(path):
        return Path(path).is_dir()
    @staticmethod
    def is_file(path):
        return Path(path).is_file()
    @staticmethod
    def stat(path):
        return Path(path).stat()
    @staticmethod
    def get_folder(path):
        return Path(path).parent
    @staticmethod
    def resolve(path):
        """Resolve a relative path to an absolute path (e.g., ../file.txt -> D:/data/file.txt)."""
        return str(Path(path).resolve())
    @staticmethod
    def get_ext(path):
        "Return the extension of the file (e.g., C:/a/b/c.txt -> .txt)."
        return Path(path).suffix
    @staticmethod
    def with_ext(path, ext):
        "Return a path with file extension replaced (e.g., C:/a/b/c.txt -> C:a/b/c.log)."
        return str(Path(path).with_suffix(ext))
    @staticmethod
    def filename(path):
        "Return the filename of path (e.g., C:/a/b/c.txt -> c.txt)."
        return Path(path).name
    @staticmethod
    def makedirs(dirpath):
        '''Create (sub)directories in the path. Do nothing if exists.'''
        try:
            os.makedirs(dirpath)
        except OSError:
            pass
    @staticmethod
    def validate_filename(s):
        """
        Return the given string converted to a string that can be used for a clean
        filename. Remove leading and trailing spaces; convert other invalid chars to
        underscores; and remove anything that is not a ASCII char.

        Args:
            s (string): the file name, NOT the path of the file.
        
        Returns:
            string: validated file name for Windows system
        """
        s=s.strip()
        invalid_chars=['"', '\\', "'", ".", "/", " ", "?", ":", "<", ">", "|", "*"]
        for char in invalid_chars:
            s=s.replace(char,'_')
        s = ''.join((c for c in s if 0 < ord(c) < 127)) # remove non-ASCII chars
        return s

def getFileList(*args, **kwargs):
    raise ValueError("getFileList function is deprecated. Please use ytZoo.FileIO.glob instead.")

def set_show_all_data():
    """Enable Jupyter Notebook to display multiple outputs in cells."""
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.ast_node_interactivity = 'all'

def multiprocess(data, worker, cores=4):
    ''' map {worker} function to each of {data}, return the aggregated result'''
    import concurrent.futures
    r = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
        for inputdata, result in zip(data, executor.map(worker, data)):
            if isinstance(result,list):
                r.extend(result)
            else:
                r.append(result)
    return r

def chunk_process_and_save(data, worker, outfilename, step=100, cores=4):
    '''process large amounts of {data} chunk by chunk using the {worker},save step results to disk'''
    from tqdm import tqdm
    def chunkit(seq, n):
        for i in range(0, len(seq), n):
            yield seq[i:i + n]
    total = len(data)
    for i,part in tqdm(list(enumerate(chunkit(data, step))),ascii=True):
        foutname = "{}_{}to{}of{}.pkl".format(outfilename,i*step,(i+1)*step,total)
        r = multiprocess(part, worker, cores)
        pkl.dump(r,foutname)
    return True

# Sequence operations #############################################    
def chunk_even(seq, num):
    'Split a sequence into evenly sized chunks'
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def chunk_size(seq, n):
    'Yield successive n-sized chunks from seq.'
    for i in range(0, len(seq), n):
        yield seq[i:i + n]

from itertools import islice
def moving_window(seq, n):
    "Returns a moving window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

###########################################################################

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def today_date():
    import datetime
    return str(datetime.date.today())
        
def cmd(commands):
    from subprocess import call
    return call(commands)

class pkl:
    @staticmethod
    def load(fname):
        with open(fname,'rb') as fin:
            return pickle.load(fin)
    @staticmethod
    def dump(data,fname):
        with open(fname,'wb') as fout:
            pickle.dump(data,fout)

class Dumper(object):
	"""Pickle a list and dump it to disk every {max_length} items."""
	def __init__(self, path='output.pkl', max_length=1000):
		self.path = path
		self.buffer = []
		self.max_length = max_length
		self._count = 0
	def __enter__(self):
		return self
	def _get_output_path(self):
		basepath, ext = os.path.splitext(self.path)
		path = "{}_{}{}".format(basepath, self._count, ext)
		return path
	def append(self, x):
		self.buffer.append(x)
		if len(self.buffer) >= self.max_length:
			self.flush()
	def extend(self, alist):
		self.buffer.extend(alist)
		if len(self.buffer) >= self.max_length:
			self.flush()
	def flush(self):
		with open(self._get_output_path(), 'wb') as fout:
			pickle.dump(self.buffer, fout)
		self.buffer = []
		self._count += 1
	def __exit__(self, type, value, traceback):
		if len(self.buffer) > 0:
			self.flush()


def logger(loggerName=None, logfile=None, stdout=True, shortDate=False, level='INFO'):
    """Return a logger that can write to stdout and a file. Replace the logger with the same name if exists.
    
    Parameters
    ----------
    stdout : bool, optional
        whether enable writing to standard output. Default is true.
    logfile : string, optional
        a file path indicating the file to write the logs. Pass None to disable writing to file. Default is None.
    loggerName : string, optional
        name of the logger. Pass None to use the module name.
    shortDate : bool, optional
        whether to use short date format. Default is False.
    level : str, optional
        specify the logging level. Default is INFO.
    
    Returns
    -------
    logger
        a logger from the built-in logging library
    """
    rootLogger = logging.getLogger(loggerName or __name__)
    for handler in rootLogger.handlers:
        handler.flush()
        handler.close()
        rootLogger.removeHandler(handler)
    rootLogger.handlers = []

    if shortDate:
        datefmt="%H:%M:%S"
    else:
        datefmt="%Y-%m-%d %H:%M:%S"
    logFormatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s",datefmt)
    # make sure we don't have duplicated handlers
    has_console_handler = has_file_handler = False
    for handler in rootLogger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            has_file_handler = True
            continue
        if isinstance(handler, logging.StreamHandler):
            has_console_handler = True
            continue
    # add a console handler if non-exists
    if stdout == True and not has_console_handler:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(0)
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
    # add file handler if non-exists
    if logfile!=None and not has_file_handler:
        fileHandler = logging.handlers.RotatingFileHandler(logfile,encoding='utf8', maxBytes=1024**3*100, backupCount=5)
        fileHandler.setLevel(0)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(level)
    return rootLogger
    
class Decorators:
    '''A collection of function decorators'''
    @staticmethod
    def cacher(f):
        '''cache the result of a function'''
        cache = {}
        def helper(x):
            if x not in cache:            
                cache[x] = f(x)
            return cache[x]
        return helper

    @staticmethod
    def tracer(f):
        '''trace the call route of a funciton'''
        def helper(*args, **kwargs):
            params=", ".join([str(li) for li in args])+\
                " ".join(",{0}={1}".format(k,kwargs[k]) for k in kwargs)
            call_str = "{0}({1})".format(f.__name__, params)
            print("Calling {0} ...".format(call_str))
            result = f(*args,**kwargs)
            print("... returning from {0} = {1}".format(
                  call_str, result))
            return result
        return helper

    @staticmethod
    def timer(f):
        '''calculate the execution time of the a function'''
        def helper(*args, **kwargs):
            params=", ".join([str(li) for li in args])+\
                " ".join(",{0}={1}".format(k,kwargs[k]) for k in kwargs)
            call_str = "{0}({1})".format(f.__name__, params)
            start_time=time.time()
            result=f(*args,**kwargs)
            milsec=int((time.time()-start_time)*1000)
            print("{0} finished in {1}ms.".format(call_str, milsec))
            return result
        return helper

def follow(thefile):
    '''follows a text file indefinitely.'''
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def WriteFile(src,dst,overwrite=False):
    FileIO.makedirs(os.path.dirname(dst))
    if os.path.isfile(dst) and overwrite==False:
        raise ValueError("File exists: {}".format(dst))
    with open(dst, 'wb') as f:
        f.write(src)
writeFile=WriteFile

def humanize_filesize(num, suffix='B'):
    '''Translate file size in bytes to human-readable representaions.'''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def xenumerate(sequence, start=1, as_pct=False):
    '''Returns a string in the format of "n/total", instead of just n. 
    This indicates the current relative position of iteration.'''
    n = start
    total=len(sequence)
    for elem in sequence:
        if not as_pct:
            s="%s/%s" % (n,total)
        else:
            s="{0:.2%}".format(n/total)
        yield s, elem
        n += 1

class ExceptionHook(object):
    instance = None
    def __call__(self, *args, **kwargs):
        if self.instance is None:
            from IPython.core import ultratb
            self.instance = ultratb.VerboseTB(call_pdb=True)
        return self.instance(*args, **kwargs)
def install_exception_hook():
    import sys
    sys.excepthook=ExceptionHook()


class using():
    """Backup the current globals(), populate it with classes and functions with in a module, and 
    restores the backup afterwards. Note that all objects created after the backup with be lost.

    Example
    =======
    import ytZoo
    with using('ytZoo'):
        soup = get_soup("https://www.google.com")
    soup
    """
    def __init__(self, module):
        self.module = module
    def __enter__(self):
        self.GLOBALS_BACKUP = globals().copy()
        self.module_dict = self.GLOBALS_BACKUP[self.module].__dict__
        globals().update(self.module_dict)
    def __exit__(self, *args, **kwargs):
        for li in self.module_dict:
            globals().pop(li)
        globals().update(self.GLOBALS_BACKUP)