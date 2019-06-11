"""Pure-python inotify interface

This provides the same basic API as the inotifyx package,
but does not require a binary installation. Notable changes
from inotifyx are that the init() call used is *always* 
the non-blocking-flagged init1 call (i.e. we always use 
non-blocking IO) and that we make events' __repr__ show the 
event flags by default.

In addition, a trivial OO facade is provided that tracks the 
watches added to an Inotify instance and uses that to provide
a bit of metadata, such as the final path-name for InotifyEvent
instances.

Example usage for the function-based API:

.. doctest::

    >>> import os,shutil,tempfile
    >>> temp = tempfile.mkdtemp(prefix='inotify-',suffix='-test')
    >>> fd = init()
    >>> final_dir = os.path.join(temp,'path','to','directory')
    >>> os.makedirs(final_dir)
    >>> wd = add_watch(fd,final_dir,IN_ALL_EVENTS)
    >>> list(get_events(fd))
    []
    >>> fh = open(os.path.join(final_dir,'test.txt'),'w')
    >>> x = fh.write('oo')
    >>> fh.close()
    >>> for event in get_events(fd):
    ...    print(event) # doctest: +ELLIPSIS
    InotifyEvent(...,...,IN_CREATE,0,'test.txt')
    InotifyEvent(...,...,IN_OPEN,0,'test.txt')
    InotifyEvent(...,...,IN_MODIFY,0,'test.txt')
    InotifyEvent(...,...,IN_CLOSE_WRITE,0,'test.txt')
    >>> list(get_events(fd,.001)) # block for up to 1ms
    []
    >>> rm_watch(fd,wd)
    >>> add_watch(fd,os.path.join(temp,'moo','roo')) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      File "/usr/lib/python2.7/doctest.py", line 1315, in __run
        compileflags, 1) in test.globs
      File "<doctest fussy.inotify[13]>", line 1, in <module>
        add_watch(fd,os.path.join(temp,'moo','roo')) # doctest: +IGNORE_EXCEPTION_DETAIL
      File "/mnt/homevar/var/pylive/fussy/fussy/inotify.py", line 115, in wrapped
        raise InotifyError( err, errno.errorcode.get(err, 'Unknown error') )
    InotifyError: [Errno 0] Unknown error
    >>> shutil.rmtree(temp)

"""
import ctypes, os, errno, sys
from functools import wraps
from ._shims import unicode

def as_8_bit(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s
def clean_repr(s):
    base = repr(s)
    while base.startswith('u'):
        base = base[1:]
    return base
NULL_BYTE = as_8_bit('\000')

class InotifyError(OSError):
    """Class for errors raised by Inotify"""

IN_ACCESS=0x00000001
IN_MODIFY=0x00000002
IN_ATTRIB=0x00000004
IN_CLOSE_WRITE=0x00000008
IN_CLOSE_NOWRITE=0x00000010
IN_OPEN=0x00000020
IN_MOVED_FROM=0x00000040
IN_MOVED_TO=0x00000080
IN_CREATE=0x00000100
IN_DELETE=0x00000200
IN_DELETE_SELF=0x00000400
IN_MOVE_SELF=0x00000800
IN_UNMOUNT=0x00002000
IN_Q_OVERFLOW=0x00004000
IN_IGNORED=0x00008000
IN_ONLYDIR=0x01000000
IN_DONT_FOLLOW=0x02000000
IN_EXCL_UNLINK=0x04000000
IN_MASK_ADD=0x20000000
IN_ISDIR=0x40000000
IN_ONESHOT=0x80000000
EVENT_NAMES = [
    'IN_ACCESS', 'IN_MODIFY', 
    'IN_ATTRIB', 'IN_CLOSE_WRITE', 
    'IN_CLOSE_NOWRITE', 'IN_OPEN', 
    'IN_MOVED_FROM', 'IN_MOVED_TO', 
    'IN_CREATE', 'IN_DELETE', 
    'IN_DELETE_SELF', 'IN_MOVE_SELF', 
    'IN_UNMOUNT', 'IN_Q_OVERFLOW', 
    'IN_IGNORED', 'IN_ONLYDIR', 
    'IN_DONT_FOLLOW', 'IN_EXCL_UNLINK', 
    'IN_MASK_ADD', 'IN_ISDIR', 
    'IN_ONESHOT', 
]

IN_CLOSE=(IN_CLOSE_WRITE | IN_CLOSE_NOWRITE)
IN_MOVE=(IN_MOVED_FROM | IN_MOVED_TO)
IN_ALL_EVENTS=(
    IN_ACCESS | IN_MODIFY | IN_ATTRIB | IN_CLOSE_WRITE |
    IN_CLOSE_NOWRITE | IN_OPEN | IN_MOVED_FROM |
    IN_MOVED_TO | IN_DELETE | IN_CREATE | IN_DELETE_SELF |
    IN_MOVE_SELF
)

IN_CLOEXEC = O_CLOEXEC = 0o02000000
IN_NONBLOCK = O_NONBLOCK = 0o00004000
NAME_MAX = 255 # from limits.h

_libc = ctypes.cdll.LoadLibrary('libc.so.6')
_libc.inotify_add_watch.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32)
_libc.inotify_add_watch.returntype = ctypes.c_int
_libc.inotify_rm_watch.argtypes = (ctypes.c_int, ctypes.c_int)
_libc.inotify_rm_watch.returntype = ctypes.c_int

class _InotifyHeader(ctypes.Structure):
    """Structure used to unpack the incoming events"""
    _fields_ = [
        ('wd', ctypes.c_int), 
        ('mask', ctypes.c_uint32), 
        ('cookie', ctypes.c_uint32), 
        ('len', ctypes.c_uint32), 
    ]
HEADER_SIZE = ctypes.sizeof(_InotifyHeader)

def raise_on_minus_one( function ):
    """Decorates function to raise InotifyError if result of function is -1
    
    TODO: so far I've never seen this return anything but 0
    from the get_errno() call, it seems likely that the errno
    is getting reset before we get around to it.
    """
    @wraps(function)
    def wrapped(*args, **named):
        result = function(*args, **named)
        err = ctypes.get_errno()
        if result == -1:
            raise InotifyError( err, errno.errorcode.get(err, 'Unknown error'),*args )
        return result 
    return wrapped

class InotifyEvent(object):
    """Encapsulates an Inotify Event instance
    
    Properties:
    
        int:fd -- inotify fd (from init())
        int:wd -- the watch which produced the event
        int:mask -- the event-mask (type) of the event, see the various IN_* constants
                    in the module for the bit-values this can take
        int:cookie -- ID which binds together events that relate to the same underlying file operation
        str:name -- filename to which the event relates
    """
    def __init__(self,fd, wd, mask, cookie, name):
        self.fd = fd 
        self.wd = wd
        self.mask = mask 
        self.cookie = cookie 
        if isinstance(name, bytes):
            name = name.decode(sys.getfilesystemencoding())
        self.name = name
    def get_event_mask(self):
        """Retrieve our event mask as a textual description"""
        keys = globals()
        result = []
        bits = self.mask
        for name in EVENT_NAMES:
            value = keys[name]
            if bits & value:
                result.append(name)
                bits = bits & (~ value)
        if bits:
            result.append(str(bits))
        return "|".join(result)
    @property
    def full_name(self):
        if hasattr(self.wd,'path'):
            if self.name:
                return os.path.join(self.wd.path,self.name)
            else:
                return self.wd.path
        return self.name
    def __repr__(self):
        return '%s(%s,%s,%s,%s,%s)'%(
            self.__class__.__name__, 
            self.fd, 
            self.wd, 
            self.get_event_mask(), 
            self.cookie, 
            clean_repr(self.full_name), 
        )
    @property
    def existing(self):
        """Does this represent an existing file, or a removed one?
        
        There are only a few events that give us "old/stale" names:
        
            IN_DELETE
            IN_DELETE_SELF
            IN_MOVED_FROM
        
        # Special case, IN_MOVE_SELF, IN_DELETE_SELF should update 
        the Inotify OO layer...
        """
        for flag in [IN_DELETE,IN_DELETE_SELF,IN_MOVED_FROM]:
            if self.mask & flag:
                return False 
        return True
    @property
    def isdir(self):
        return self.mask & IN_ISDIR
    @property
    def removed(self):
        return self.mask & IN_MOVED_FROM or self.mask & IN_DELETE

@raise_on_minus_one
def init(flags=O_NONBLOCK):
    """Initialize (produce a file descriptor for watching inotify events)"""
    return _libc.inotify_init1(flags)
@raise_on_minus_one
def add_watch(fd, path, mask=IN_ALL_EVENTS):
    """Add a watch for the given path to the fd"""
    return _libc.inotify_add_watch(fd, as_8_bit(path), mask)
@raise_on_minus_one
def rm_watch(fd, wd):
    """Remove the watch wd from the inotify file descriptor fd
    
    If successful an IN_IGNORED event will be generated on the fd
    """
    result = _libc.inotify_rm_watch(fd, wd)
    if result:
        return result
def get_events(fd, block=None, period=None):
    """Retrieve all events currently available
    
    block -- if None, do not block, only return already-available events
             otherwise pass as the period argument to select.select
             to wait for up to that long for an event to become available
    period -- if None, use default blocking period, otherwise 
    
    yields InotifyEvent instances for all available events
    """
    if block or period:
        return get_events_blocking( fd, poll_period=period or 5.0 )
    else:
        return get_events_nonblocking( fd )
def get_events_blocking(fd, poll_period=5.0):
    """Get pending events, waiting up to poll_period for events to show up"""
    import select 
    if hasattr( select, 'epoll' ):
        poll = select.epoll()
    else:
        poll = select.poll()
    poll.register( fd, select.EPOLLIN|select.EPOLLPRI|select.EPOLLERR|select.EPOLLHUP )
    try:
        while True:
            try:
                for _,_ in poll.poll( poll_period ):
                    for event in get_events_nonblocking( fd ):
                        yield event
                # Orderly exit
                break
            except (IOError,OSError) as err:
                if err.errno not in (errno.EWOULDBLOCK,errno.EINTR):
                    raise
    finally:
        poll.unregister( fd )
    
def get_events_nonblocking(fd):
    """Non-blocking version of get-events, but does *not* wait for events"""
    try:
        read_length = HEADER_SIZE + NAME_MAX + 1
        while True:
            data = os.read(fd, read_length)
            while data:
                header = _InotifyHeader.from_buffer_copy(data)
                name = data[HEADER_SIZE:HEADER_SIZE+header.len]
                if name:
                    name = name[:name.index(NULL_BYTE)]
                data = data[HEADER_SIZE+header.len:]
                yield InotifyEvent(fd, header.wd,header.mask, header.cookie, name) 
    except (IOError,OSError) as err:
        if err.errno not in (errno.EWOULDBLOCK,errno.EINTR):
            raise
    

class Inotify(int):
    """OO facade over the Inotify API
    
    .. doctest::
    
        >>> import os,shutil,tempfile
        >>> temp = tempfile.mkdtemp(prefix='inotify-',suffix='-test')
        >>> fd = Inotify()
        >>> final_dir = os.path.join(temp,'path','to','directory')
        >>> os.makedirs(final_dir)
        >>> wd = fd.add_watch(final_dir,IN_ALL_EVENTS)
        >>> wd.__class__.__name__
        'Watch'
        >>> list(fd.get_events())
        []
        >>> fh = open(os.path.join(final_dir,'test.txt'),'w')
        >>> x = fh.write('oo')
        >>> fh.close()
        >>> for event in fd.get_events():
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_CREATE,0,'.../inotify-...-test/path/to/directory/test.txt')
        InotifyEvent(...,...,IN_OPEN,0,'.../inotify-...-test/path/to/directory/test.txt')
        InotifyEvent(...,...,IN_MODIFY,0,'.../inotify-...-test/path/to/directory/test.txt')
        InotifyEvent(...,...,IN_CLOSE_WRITE,0,'.../inotify-...-test/path/to/directory/test.txt')
        >>> list(fd.get_events(.001)) # block for up to 1ms
        []
        >>> os.rename(final_dir,final_dir+'.bak')
        >>> for event in fd.get_events():
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_MOVE_SELF,0,'.../inotify-...-test/path/to/directory')
        >>> fd.rm_watch(wd) # doctest: +SKIP
        1
        >>> fd.add_watch(os.path.join(temp,'moo','roo')) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          File "/usr/lib/python2.7/doctest.py", line 1315, in __run
            compileflags, 1) in test.globs
          File "<doctest fussy.inotify[13]>", line 1, in <module>
            fd.add_watch(os.path.join(temp,'moo','roo')) # doctest: +IGNORE_EXCEPTION_DETAIL
          File "/mnt/homevar/var/pylive/fussy/fussy/inotify.py", line 115, in wrapped
            raise InotifyError( err, errno.errorcode.get(err, 'Unknown error') )
        InotifyError: [Errno 0] Unknown error
        >>> fd.close()
        >>> shutil.rmtree(temp)
    
    """
    closed = False
    def __new__(cls,flags=O_NONBLOCK):
        """Create a new Inotify by calling init() and wrapping the result"""
        base = init(flags)
        return super(cls,Inotify).__new__(cls,base)
    def __init__(self):
        """Initialize our internal structures"""
        self.watches = {}
    def add_watch(self,path, mask=IN_ALL_EVENTS):
        """Add a watch for the given path to the Inotify
        
        path -- file-path to add to tracking
        mask -- bitwise or-ing of the flags in which we are interested
        
        returns the wrapped Watch instance for the new watch
        """
        base = add_watch(self,path,mask)
        watch = self.watches[base] = Watch(base,fd=self,path=path,mask=mask)
        return watch
    def rm_watch(self,wd):
        """Remove the watch wd from the inotify file descriptor fd
        
        If successful an IN_IGNORED event will be generated on the fd
        
        wd -- either a simple integer or a Watch instance
        
        returns the internally tracked watch (or wd if not tracked internally)
        """
        try:
            watch = self.watches.pop(wd)
        except KeyError:
            watch = wd
        rm_watch(self,wd)
        return watch
    def get_events(self,*args,**named):
        """Retrieve all events currently available
        
        block -- if None, do not block, only return already-available events
                 otherwise pass as the period argument to select.select
                 to wait for up to that long for an event to become available
        period -- if passed, the duration to wait for an event (assumes blocking)
        
        yields InotifyEvent instances for all available events
        with the fd and wd fields referencing this Inotify and 
        any wd registered with add_watch on this instance.
        """
        for event in get_events(self,*args,**named):
            event.fd = self 
            event.wd = self.watches.get(event.wd,event.wd)
            # TODO: if event.mask & IN_ONESHOT we should de-register
            # the wd after the first cookie we see that uses that 
            # wd is exausted, that is, after all events with that cookie
            # have been seen...
            yield event
    def close(self):
        """Close our file descriptor"""
        os.close(self)
        self.closed = True

class Watch(int):
    """Wraps watch instances
    
    Simply provides metadata about the watch so that users can see
    the flags, path, etc used in the watch
    """
    def __new__(cls,base,fd,path,mask):
        """Create the new watch instance
        
        base -- base wd (watch id) value
        fd -- the Inotify instance
        path -- our path as passed to add_watch
        mask -- the mask used to create our watch
        """
        base = super(Watch,cls).__new__(cls,base)
        base.fd = fd
        base.path = path 
        base.mask = mask
        return base
