from __future__ import absolute_import, division, print_function
import sys
import time
import warnings
import matplotlib.pyplot as plt
from matplotlib import transforms
from itertools import takewhile

# Compatability for python3
if getattr(sys.version_info, 'major') == 3:
    xrange = range

#Define alphabet
alphabet = list('abcdefghijklmnopqrstuvwxyz')

# Specify the time when module was initalised. Used in progress if
# t_initial was not specified.
t_initial_master = time.time()

# Used for progress class
eps = sys.float_info.epsilon

class ProgressWarning(UserWarning):
    """Issued when results may be unstable."""
    pass

# On import, make sure that InstabilityWarnings are not filtered out.
warnings.simplefilter('always', ProgressWarning)

class prettyfloat(object):
    """returns a truncated float of 2 decimal places.
    
    Example
    -------
    use: map(prettyfloat, x) for a list, x
    
    Reference
    ---------
    https://stackoverflow.com/a/1567630
    """
    
    def __init__(self, float, dec=6):
        """dec = precision of float"""
        
        self.float=float
        self.dec=dec

    def __repr__(self):
        return "%0.*f" % (self.dec, self.float)

class progress(object):
    """
    Outputs the progress of interable (e.g. loop) to the console.
    
    Examples
    --------
    >>> size = 10
    >>> message = "Hello %s. My name is %s"
    >>> with gu.progress(message, size) as progress:
    >>>     for i in xrange(size):
    >>>         time.sleep(.5)
    >>>         progress.update("James", "Brian")
    """

    def __init__(self, msg, size, confirmation=True):
        """
        Makes a note of the time progress was called.
        
        Parameters
        ----------
        size : int
            the size of the iterator to progress
        """

        # Initalise parameters
        self.t_initial = time.time()
        self.msg = str(msg)
        self.size = int(size)
        self.i = 0
        self.confirmation = confirmation

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):

        # Remove last line in command line
        sys.stdout.write("\033[K")
        
        # Output the final message to user
        if self.confirmation:
            cprint("[INFO] Iterator Completed (In %.4fs)" \
                    % (time.time() - self.t_initial))
        
    def _timestats(self):
        """
        Calculate the time statistics of the iterator.
        """

        t_elapsed = time.time() - self.t_initial
        t_remain  = (t_elapsed / (self.i + eps)) * \
                    (self.size - self.i + eps)

        return t_elapsed, t_remain

    def _message(self, args):
        """
        Build message to print to output.
        """

        full_message = "[INFO] Time Elapsed: %.0fs. Time Remaining: %.0fs. " \
                         + self.msg + "\r"
        sys.stdout.write(full_message % tuple(args))
        sys.stdout.flush()

    def _error(self):
        """
        Check if iterator has gone above size originally specified.
        """

        # Increment iterator
        self.i += 1

        if self.i > self.size:
            warnings.warn("size of progress was not specified correctly. " \
                          "You'll notice negative values in time remaining!", 
                          ProgressWarning, stacklevel=3)

    def update(self, *args):
        """
        Update the progress of the iterator.
        """

        # Remove last line in command line
        sys.stdout.write("\033[K")

        # Calculate time statistics
        t_elapsed, t_remain = self._timestats()

        # Build message
        self._message(_flat((t_elapsed, t_remain, args)))

        # Error checker
        self._error()

def _flat(array, level=1):
    """
    Flatten a list of (lists of (lists of strings)) for any level 
    of nesting
    
    Parameters
    ----------
    array : array_like, string
        An array_like object containing all string values.
    level : int, optional
        The number of nested levels to remove. Specify -1 to removed all
        nests automatically.
        
    Returns
    -------
    x : generator
        The flattened array is returned as a generator. Use as an 
        iterator, or used list(x) to return values.
    
    Reference
    ---------
    https://stackoverflow.com/a/17864492
    https://stackoverflow.com/a/5286571/8765762
    
    Notes
    -----
    Only works with both Python 2.x and 3.x
    
    """
    
    for x in array:
        
        # If desired level of nesting reached, yield x
        if level == 0:
            yield x
        
        # Else if not a string level, go down another level
        elif hasattr(x, '__iter__') and not isinstance(x, str):
            for y in _flat(x, level=level-1):
                yield y

        # If at string level, then yield x
        else:
            yield x


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return list(subclasses)
   
def rainbow_text(x, y, strings, colors, ax=None, **kw):
    """
    Take a list of ``strings`` and ``colors`` and place them next to each
    other, with text strings[i] being shown in colors[i].

    This example shows how to do both vertical and horizontal text, and will
    pass all keyword arguments to plt.text, so you can set the font size,
    family, etc.

    The text will get added to the ``ax`` axes, if provided, otherwise the
    currently active axes will be used.
    """

    if ax is None:
        ax = plt.gca()
    t = ax.transData
    canvas = ax.figure.canvas

    # horizontal version
    for s, c in zip(strings, colors):
        text = ax.text(x, y, s + " ", color=c, transform=t, **kw)
        text.draw(canvas.get_renderer())
        ex = text.get_window_extent()
        t = transforms.offset_copy(text._transform, x=ex.width, units='dots')

    # vertical version
    for s, c in zip(strings, colors):
        text = ax.text(x, y, s + " ", color=c, transform=t,
                        rotation=90, va='bottom', ha='center', **kw)
        text.draw(canvas.get_renderer())
        ex = text.get_window_extent()
        t = transforms.offset_copy(text._transform, y=ex.height, units='dots')
        
def cprint(*args, **kwargs):
    """Prints colourful messages under a standard style set.
    
    Update: Now handles in the same as does print, meaning you
    can give print as many input strings as you want. e.g.
        
    >>> cprint("Hello", "Brian", "Simon")
    Hello Brian Simon    #but in bold
    
    >>> print("Hello", "Brian", "Simon")
    Hello Brian Simon
    
    No need to specifiy kind anymore. Now defaults to bold.
    Also give kwargs to the print statement now such as 'file'.
    N.B. supplying end in cprint will cause an error as that is
    already being used in this function when print is called."""
    
    #Console Colours
    bcolours = {
        "header" : '\033[95m',
        "okblue" : '\033[94m',
        "okgreen" : '\033[92m',
        "warning" : '\033[31m',
        "fail" : '\033[91m',
        "endc" : '\033[0m',
        "bold" : '\033[1m',
        "underline" : '\033[4m'}
    
    type = kwargs.pop('type', "bold")
    
    for message in args:
        print(bcolours[type] + message + bcolours['endc'], end=' ', **kwargs)
    print("\r")
    
def rgb2hex(r,g,b):
    """Converts RGB values into Hexadecimal
    
    Reference
    ---------
    
    https://stackoverflow.com/a/43572620/8765762
    """
    
    return "#{:02x}{:02x}{:02x}".format(r,g,b)        

def readcomments(filename, comment='#'):
    """
    Reads in filename and extracts only data that contains the comments
    parameter.
    
    Reference
    ---------
    https://stackoverflow.com/a/39724905/8765762
    """
            
    comments_all = []
    with open(filename,'r') as cmt_file:    # open file
        for line in cmt_file:    # read each line
            if line[0] == comment:    # check the first character
                comments_all.append(line[1:])    # remove first '#'

    return comments_all    

