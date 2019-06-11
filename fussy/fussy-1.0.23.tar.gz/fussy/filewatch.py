import logging, re, os, fnmatch
from . import inotify 
log = logging.getLogger(__name__)

class FileWatcher(object):
    """Watches a directory for files matching fnmatch
    
    Assumes that all file-writes will be done with twrite,
    and by default assumes that ~ suffixed files should not 
    be processed (again, the twrite default temp-file suffix).
    
    .. doctest::
    
        >>> import os,shutil,tempfile
        >>> from fussy import twrite
        >>> temp = tempfile.mkdtemp(prefix='filewatcher-',suffix='-test')
        >>> with open(os.path.join(temp,'test.moo'),'wb') as fh:
        ...    written = fh.write(b'a')
        >>> f = FileWatcher( temp, recursive=True )
        >>> for event in f.start():
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_CREATE,0,'.../filewatcher-...-test/test.moo')
        >>> with open(os.path.join(temp,'test2.txt'),'wb') as fh:
        ...    written = fh.write(b'a')
        >>> for event in f.iterate_events(None): # do not block
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_CREATE,0,'.../filewatcher-...-test/test2.txt')
        >>> twrite.twrite( os.path.join(temp,'ieee','zoom'),'content')
        >>> for event in f.iterate_events(None): # do not block
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_CREATE|IN_ISDIR,0,'.../filewatcher-...-test/ieee')
        InotifyEvent(...,...,IN_CREATE,0,'.../filewatcher-...-test/ieee/zoom')
        >>> shutil.rmtree( os.path.join(temp,'ieee'))
        >>> for event in f.iterate_events(None): # do not block
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_DELETE,0,'.../filewatcher-...-test/ieee/zoom')
        InotifyEvent(...,...,IN_DELETE|IN_ISDIR,0,'.../filewatcher-...-test/ieee')
        >>> f.unwatch_directory( '/moo' ) # won't do anything, as it's not watched...
        >>> f.close()
        >>> f2 = FileWatcher(temp,pattern='*.moo',recursive=False)
        >>> for event in f2.start():
        ...    print(event) # doctest: +ELLIPSIS
        InotifyEvent(...,...,IN_CREATE,0,'.../filewatcher-...-test/test.moo')
        >>> shutil.rmtree(temp)
    
    """
    # maximum time before we iterate to avoid infinite hangs
    POLL_PERIOD = 20
    DEFAULT_EVENTS = (
        inotify.IN_MOVE|inotify.IN_MODIFY|
        inotify.IN_CREATE|inotify.IN_DELETE|
        inotify.IN_MOVED_TO|inotify.IN_MOVED_FROM
    )
    active = False
    def __init__(
        self,
        directory,
        pattern=re.compile(r'.+[^~]$'),
        events = None,
        recursive = False,
    ):
        """Watch directory for files matching pattern
        
        directory -- path to a directory
        pattern -- fnmatch string *or* regex object for matching
        """
        self.pattern = pattern
        self.directories = [directory]
        self.watches = {}
        self.back_watches = {}
        if events is None:
            events = self.DEFAULT_EVENTS
        self.events = events
        self.recursive = recursive
    
    def match(self, filename ):
        """Does this filename match our patterns?"""
        if hasattr(self.pattern,'match'):
            return self.pattern.match(filename)
        else:
            return fnmatch.fnmatchcase(os.path.basename(filename),self.pattern)
    
    _fd = None
    @property
    def fd(self):
        if self._fd is None:
            self._fd = inotify.Inotify()
        return self._fd
    def fileno(self):
        return self.fd
    
    def watch_directory(self,directory):
        if directory not in self.directories:
            self.directories.append(directory)
        if self.active and directory not in self.watches:
            log.info('Start watching: %s', directory)
            wd = self.watches[directory] = self.fd.add_watch(
                directory, 
                self.events,
            )
            log.debug('Watch: %s -> %s,%s',directory,int(self.fd),int(wd))
            return wd
    def unwatch_directory(self,directory,deleted=False):
        """De-register watches on given directory"""
        try:
            log.info('Stop watching: %s', directory)
            wd = self.watches.pop(directory)
        except KeyError:
            pass 
        else:
            try:
                self.fd.rm_watch(wd)
            except Exception as err:
                if hasattr(err,'errno') and err.errno == 22:
                    pass 
                elif not deleted:
                    log.warning('Failure during removal %s: %s', err,directory)
        while directory in self.directories:
            self.directories.remove(directory)
        prefix = directory + os.path.sep
        if prefix.endswith( os.path.sep *2 ):
            prefix = prefix[:-1]
        log.debug("Checking for prefix: %s",prefix)
        for subdir in [
            s for s in self.directories 
            if s.startswith( prefix )
        ]:
            self.unwatch_directory(subdir)
        
    def __iter__(self):
        log.info('Starting file watcher')
        try:
            for event in self.start():
                yield event
            while self.active:
                for event in self.iterate_events(self.POLL_PERIOD):
                    yield event
        finally:
            self.close()
    def start(self):
        """Start up our iterations
        
        yields create events for each matching file...
        """
        self.active = True
        for event in self.initial_watches():
            yield event
    def close(self):
        """Close our watches and shut down"""
        fd = self._fd 
        if fd:
            fd.close()
        self.watches.clear()
        self.active = False
        
    def initial_watches(self):
        """Walk our directories adding them to our watcher"""
        for directory in self.directories:
            for match in self.on_directory_added(directory):
                yield match
    def iterate_events(self,period=None):
        """Do a single iteration of polling for events for a given period (blocking)
        
        This interface is intended to be used from a thread, so that you 
        get a simple iterable producing events to be processed. The processing
        for each event should be relatively lightweight, as it needs to 
        return fast enough to avoid having the event queue back up.
        """
        events = self.fd.get_events(block=True,period=period or self.POLL_PERIOD)
        events = [
            e for e in events 
            if not (
                (e.mask & inotify.IN_IGNORED) or (e.mask & inotify.IN_DELETE_SELF)
            )
        ]
        for event in events:
            fullname = event.full_name
            if event.isdir:
                yield event
                if self.recursive:
                    if event.mask & inotify.IN_DELETE or event.mask & inotify.IN_MOVED_FROM:
                        self.on_directory_deleted( fullname )
                    elif event.mask & inotify.IN_CREATE or event.mask & inotify.IN_MOVED_TO:
                        for match in self.on_directory_added( fullname ):
                            yield match
            elif event.mask & inotify.IN_DELETE_SELF:
                log.debug('Watched directory removed: %s',fullname )
            elif self.match( fullname ):
                yield event
        
    
    def on_directory_deleted(self,directory):
        """A directory has been deleted"""
        self.unwatch_directory( directory, deleted=True )
    def on_directory_added(self,directory):
        """A directory has been created"""
        if self.recursive:
            for base,subdirs,files in os.walk(directory):
                wd = self.watch_directory( os.path.join(directory,base) )
                if wd:
                    for file in files:
                        fullname = os.path.join(base,file)
                        if self.match(fullname):
                            yield inotify.InotifyEvent(
                                fd = self.fd,
                                wd = wd,
                                mask=inotify.IN_CREATE,
                                cookie=0,
                                name=file,
                            )
        else:
            wd = self.watch_directory( directory )
            if wd:
                for file in os.listdir(directory):
                    fullname = os.path.join(directory,file)
                    if self.match(fullname):
                        yield inotify.InotifyEvent(
                            fd = self.fd,
                            wd = wd,
                            mask=inotify.IN_CREATE,
                            cookie=0,
                            name=file,
                        )

def options():
    """Create the options for demonstration watcher
    
    .. doctest::
    
        >>> parser = options()
        >>> args = parser.parse_args(['--recursive','/tmp/test'])
        >>> args.recursive
        True
        >>> args.target
        '/tmp/test'
    
    """
    import argparse
    parser = argparse.ArgumentParser(description='Watch directory for files matching given regex')
    parser.add_argument(
        '--recursive', action='store_true',
        default=False,
        help='Recursively watch all directories under the directory'
    )
    parser.add_argument(
        'target', metavar='DIR',
        help="Target directory to watch (must exist)",
    )
    return parser
    
def main():
    logging.basicConfig(level=logging.INFO)
    args = options().parse_args()
    r = FileWatcher( args.target, recursive=args.recursive, )
    for event in r:
        log.info('%r', event)
