"""Provide a cron lock for preventing cron-bombs and the like"""
import os, logging, fcntl, errno, signal, tempfile, time, threading
log = logging.getLogger( __name__ )

def time_function( marker=None ):
    from functools import wraps
    def wrapper( function ):
        if marker is None:
            final_marker = '%s.%s'%(function.__module__,function.__name__)
        else:
            final_marker = marker
        @wraps( function )
        def timer( *args, **named ):
            start = time.time()
            try:
                holder = open( '/var/firmware/run/request-localhost-8111.lock' ).read()
            except Exception:
                holder = None
            try:
                return function( *args, **named )
            finally:
                log.info("%s: %0.1fs by %s", final_marker, time.time() - start, holder )
        return timer
    return wrapper

class Busy( IOError ):
    """Raised if the lock is held by another cronlock"""
class Timeout( RuntimeError ):
    """Raised if the timeout signal triggers"""
class AlreadyHeld( Busy ):
    """Raised if we attempt to lock multiple times from the same process"""
    
class Flock( object ):
    """A context manager that just flocks a file"""
    file = None
    def __init__( self, filename, blocking=False ):
        self.filename = filename 
        self.blocking = blocking
    def __str__( self ):
        return '%s( %r )'%( self.__class__.__name__, self.filename )
    def __enter__( self ):
        if self.file:
            raise Busy( """Attempted to lock the %s twice"""%( self ))
        fh = open( self.filename, 'ab+' )
        for i in range(2): # limited number of retries
            try:
                flags = fcntl.LOCK_EX
                if not self.blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock( fh, flags ) # can raise IOError 
            except IOError as err:
                if err.errno == errno.EWOULDBLOCK:
                    other_pid = None
                    if os.path.exists(self.filename):
                        try:
                            other_pid = int(open(self.filename).readline())
                        except Exception:
                            pass
                        else:
                            from fussy import processcontrol 
                            if os.getpid() == other_pid:
                                raise AlreadyHeld(
                                    "Multiple attempts to lock the same file from the same process %s"%(self.filename)
                                )
                            if not processcontrol.alive( other_pid ):
                                log.info(
                                    "PID#%s held the lock on %s, but does not appear to be alive, retrying",
                                    other_pid,
                                    self.filename,
                                )
                                continue
                            
                    err = Busy( *(err.args + ('held by PID#%s'%(other_pid,), )) )
                    err.errno = errno.EWOULDBLOCK
                raise err
        fh.seek( 0 ) # rewind to start...
        fh.write( (u'%s\n'%(os.getpid())).encode('utf-8'))
        fh.flush()
        self.file = fh
        return fh
    def __exit__( self, *args ):
        try:
            fh = self.__dict__.pop( 'file' )
        except KeyError:
            log.warning("No 'file' member in lock, somehow exiting before entry completed?")
        else:
            try:
                os.remove(self.filename)
            except (OSError, IOError):
                log.warning('File %s removed while locked', self.filename)
            fcntl.flock( fh, fcntl.LOCK_UN )
            fh.close()
    def write( self, *args ):
        with self:
            return self._write(*args)
    def _write(self,*args):
        self.file.seek(0)
        self.file.write( *args )
        self.file.flush()
    def read( self, *args ):
        with self:
            return self._read(*args)
    def _read(self, *args):
        return self.file.read( *args )

class Lock( object ):
    """A Context manager that provides cron-style locking"""
    def __init__( self, lockfile ):
        """Create a lock file 
        
        name -- used to construct the lock-file name 
        directory -- directory in which to construct the lock-file 
        """
        self.flock = Flock( lockfile )
    @property 
    def pid( self ):
        return os.getpid()
    def __enter__( self ):
        self.flock.__enter__()
    def __exit__( self, *args ):
        self.flock.__exit__(*args)
    def on_timeout( self, *args, **named ):
        raise Timeout( "Maximum run-time exceeded, aborting" )
    def set_timeout( self, duration ):
        """Set a signal to fire after duration and raise an error"""
        signal.signal( signal.SIGALRM, self.on_timeout )
        signal.alarm( int(duration) )

class ThreadLock(object):
    """Simple context manager for a threading RLock"""
    def __init__(self, lock_wait=5):
        self._lock = threading.RLock()
        self.lock_wait = lock_wait
    def __enter__(self):
        start = time.time()
        abort = start + self.lock_wait
        while time.time() < abort:
            if not self._lock.acquire(blocking=False):
                time.sleep(max(
                    (
                        (abort-time.time())/100., 
                        0.00001
                    ), 
                ))
            else:
                #log.debug("Acquired thread lock after: %0.3fs", time.time()-start)
                return self
        raise Busy('Timeout waiting for thread lock')
    def __exit__(self, *args):
        self._lock.release()

class BlockingLock( Lock ):
    """Lock class that blocks for up to lock_wait seconds waiting for other process to exit
    
    Also uses ThreadLock to prevent multiple threads from 
    this process from running simultaneously...
    """
    def __init__( self, lockfile, lock_wait=5 ):
        super( BlockingLock, self ).__init__( lockfile )
        self._threadlock = ThreadLock()
        self.lock_wait = lock_wait
    def __enter__( self ):
        start = time.time()
        abort = start + self.lock_wait
        while time.time() < abort:
            try:
                result = super( BlockingLock, self ).__enter__()
                delta = time.time() - start 
                if delta > .1:
                    log.info("Acquired after %0.1fs",delta)
                return result 
            except Busy:
                max_wait = .01
                duration = max(
                    (
                        min(( 
                            (abort-time.time())/100.,
                            max_wait,
                        )), 
                        0.00001
                    ), 
                )
                time.sleep(duration)
        log.debug("Timeout waiting")
        raise Busy( "Lock on %s timed out"%( self.flock.filename ))

def with_lock( name, directory=None, timeout=None ):
    """Decorator that runs a function with Lock instance acquired
    
    * name -- basename of the file to create 
    * directory -- if specified, the directory in which to store files, 
        defaults to tempfile.gettempdir()
    * timeout -- if specified, the number of seconds to allow before raising 
        a Timeout error
    """
    if directory is None:
        directory = tempfile.gettempdir()
    filename = os.path.join( directory, name )
    lock = Lock( filename )
    def wrap_func( function ):
        """Wraps the function execution with our lock"""
        def wrapped_with_lock( *args, **named ):
            with lock:
                if timeout:
                    lock.set_timeout( timeout )
                return function( *args, **named )
        wrapped_with_lock.__name__ = function.__name__
        wrapped_with_lock.__doc__ = function.__doc__
        wrapped_with_lock.__dict__ = function.__dict__
        wrapped_with_lock.lock = lock 
        return wrapped_with_lock
    return wrap_func
