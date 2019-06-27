import random
import inspect
import string
import shutil
import re
import keyword
import ast
import readline
from datetime import timedelta

import numpy as np

from swutil.validation import String, Integer

class no_context:
    def __enter__(self, *args):
        pass
    def __exit__(self, *args):
        pass

def smart_range(*args):
    '''
    smart_range(1,3,9)==[1,3,5,7,9]
    '''
    if len(args)==1:#String
        string_input = True
        string = args[0].replace(' ','')
        original_args=string.split(',')
        args = []
        for arg in original_args:
            try:
                args.append(ast.literal_eval(arg))
            except (ValueError,SyntaxError):
                try:# Maybe an arithmetic expression?
                    args.append(eval(arg,{'__builtins__':{}}))
                except (NameError,SyntaxError):#Input was actually meant to be a string, e.g. smart_range('a,...,z'), or input was interval type, e.g. smart_range('[1,3]/10')
                    args.append(arg)
    else:
        string_input = False
    arg_start = args[0]
    if len(args)>2:
        arg_step = args[1]
        if len(args)>3:
            raise ValueError('At most 3 arguments: start, step, stop')
    else:
        arg_step = None
    arg_end = args[-1]
    if String.valid(arg_start) and len(arg_start)==1:#Character
        range_type = 'char'
    elif all(Integer.valid(arg) for arg in args):
        range_type = 'integer'
    else: 
        if string_input and original_args[0][0] in ['(','[']:
            range_type = 'linspace'
        else:
            range_type = 'float'

    if range_type == 'char':
        start = ord(arg_start)
        step = (ord(arg_step)- start) if arg_step else 1
        end = ord(arg_end)
        out = [chr(i) for i in range(start,end+step,step)]
        if np.sign(step)*(ord(out[-1])-end)>0:
            del out[-1]
        return out
    elif range_type == 'integer':
        if string_input:
            if len(args)==2 and all('**' in oa for oa in original_args):#Attempt geometric progresesion
                bases,exponents = zip(*[oa.split('**') for oa in original_args])
                if len(set(bases))==1:#Keep attempting geometric progression
                    return [int(bases[0])**exponent for exponent in smart_range(','.join(exponents))]
        start = arg_start
        step = (arg_step - arg_start) if arg_step is not None else 1
        end = arg_end
        out = list(range(start,end+step,step))
        if np.sign(step)*(out[-1]-end)>0:
            del out[-1]
        return out
    elif range_type == 'float':
        if len(args)==2 and all('**' in oa for oa in original_args):#Attempt geometric progresesion
            bases,exponents = zip(*[oa.split('**') for oa in original_args])
            if len(set(bases))==1:#Keep attempting geometric progression
                return [float(bases[0])**exponent for exponent in smart_range(','.join(exponents)) ]
        if len(args) == 2:
            raise ValueError()
        start = arg_start
        step = arg_step - arg_start
        end = arg_end
        out = list(np.arange(start,end+1e-12*step,step))
        return out
    elif range_type == 'linspace':
        lopen,start = (original_args[0][0]=='('),float(original_args[0][1:])
        end,N = original_args[1].split('/')
        end,ropen = float(end[:-1]),(end[-1]==')')
        N = ast.literal_eval(N)+lopen +ropen
        points = np.linspace(start,end,num=N)
        return points[lopen:len(points)-ropen]

def ld_to_dl(ld):
    '''
    Convert list of dictionaries to dictionary of lists
    '''
    if ld:
        keys = list(ld[0])
        dl = {key:[d[key] for d in ld] for key in keys}
        return dl
    else:
        return {}

def isdebugging():
    for frame in inspect.stack():
        if frame[1].endswith('pydevd.py') or frame[1].endswith('pdb.py'):
            return True
    return False

def chain(*fs):
    '''
    Concatenate functions
    '''
    def chained(x):
        for f in reversed(fs):
            if f:
                x=f(x)
        return x
    return chained

def string_dialog(title,label):
    import tkinter
    import tkinter.simpledialog
    root = tkinter.Tk()
    root.withdraw()#Somehow this is sometimes needed to prevent errors about something in Tk not existing yet
    return tkinter.simpledialog.askstring(title, label)

def raise_exception(title):
    raise Exception(title)

def cmd_exists(cmd):
    '''
    Check whether given command is available on system
    '''
    return shutil.which(cmd) is not None

def split_integer(N,bucket = None, length = None):
    if bucket and not length:
        if bucket <1:
            raise ValueError()
        length = N//bucket + (1 if N%bucket else 0)
    if length ==0:
        if N ==0:
            return []
        else:
            raise ValueError()
    tmp = np.array([N//length]*length)
    M = N % length
    tmp[:M]+=1
    return list(tmp)

def split_list(l,N):
    '''
    Subdivide list into N lists
    '''
    npmode = isinstance(l,np.ndarray)
    if npmode:
        l=list(l)
    g=np.concatenate((np.array([0]),np.cumsum(split_integer(len(l),length=N))))
    s=[l[g[i]:g[i+1]] for i in range(N)]
    if npmode:
        s=[np.array(sl) for sl in s]
    return s

def random_string(length):
    '''
    Generate alphanumerical string. Hint: Check whether module tempfile has what you want, especially when you are concerned about race conditions
    '''
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def random_word(length,dictionary = False):#may return offensive words if dictionary = True
    '''
    Creates random lowercase words from dictionary or by alternating vowels and consonants
    
    The second method chooses from 85**length words.
    The dictionary method chooses from 3000--12000 words for 3<=length<=12
    (though this of course depends on the available dictionary)
    
    :param length: word length
    :param dictionary: Try reading from dictionary, else fall back to artificial words
    '''
    if dictionary:
        try:
            with open('/usr/share/dict/words') as fp:
                words = [word.lower()[:-1] for word in fp.readlines() if re.match('[A-Za-z0-9]{}$'.format('{'+str(length)+'}'),word)]
            return random.choice(words)
        except FileNotFoundError:
            pass
    vowels = list('aeiou')
    consonants = list('bcdfghklmnprstvwz')
    pairs = [(random.choice(consonants),random.choice(vowels)) for _ in range(length//2+1)] 
    return ''.join([l for p in pairs for l in p])[:length]

def string_from_seconds(seconds):
    '''
    Converts seconds into elapsed time string of form 
    
    (X days(s)?,)? HH:MM:SS.YY
    
    '''
    td = str(timedelta(seconds = seconds))
    parts = td.split('.')
    if len(parts) == 1:
        td = td+'.00'
    elif len(parts) == 2:
        td = '.'.join([parts[0],parts[1][:2]])
    return td

def input_with_prefill(prompt, text):
    '''
    https://stackoverflow.com/questions/8505163/is-it-possible-to-prefill-a-input-in-python-3s-command-line-interface
    '''
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    try:
        readline.set_pre_input_hook(hook)
    except Exception:
        pass
    result = input(prompt)
    try:
        readline.set_pre_input_hook()
    except Exception:
        pass
    return result

def identity(x):
    return x

def is_identifier(s):
    '''
    Check if string is valid variable name
    '''
    return s.isidentifier() and not keyword.iskeyword(s)

