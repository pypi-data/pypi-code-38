"""Tail protocol for files using Twisted non-blocking IO"""
import os, sys, errno
from twisted.internet import fdesc, reactor
from twisted.python import log

from twisted.internet import inotify
from twisted.python import filepath

class FileTail( object ):
    def __init__(self,filename ):
        if hasattr(filename,'path'):
            filename = filename.path
        self.filename = filename
        self.buffer = ''
    def start_watching(self):
        # TODO: allow for handling log rotation etc.
        # TODO: use the overall directory inotify instead,
        # and use *that* to do log-rotation checks...
        self.notifier = inotify.INotify()
        self.notifier.startReading()
        self.notifier.watch(
            filepath.FilePath(self.filename), 
            mask = inotify.IN_MODIFY,
            callbacks=[self.on_file_change],
        )
    _fd = None
    @property
    def fd(self):
        if self._fd is None:
            self._fd = os.open(self.filename,os.O_RDONLY )
            fdesc.setNonBlocking( self._fd )
        return self._fd
    def on_file_change(self,ignored, filepath, mask):
        if mask & inotify.IN_MODIFY:
            self.read_from_file()
    def read_from_file(self):
        fd = self.fd
        while True:
            # TODO: really, we should do a non-blocking producer 
            # using an abstract file handle, but as that turns 
            # out not to usefully restrict us on EOF it's kinda 
            # loopy...
            # For the simple "tail a file to web browser" case 
            # this should work...
            try:
                output = os.read( fd, 8192 )
            except  (OSError, IOError) as err:
                if err.args[0] in (errno.EAGAIN, errno.EINTR):
                    pass
                elif err.args[0] in errno.EWOULDBLOCK:
                    # can't read any more
                    break
                else:
                    log.msg("Error reading from %s"%(self.name,))
                    self._fd = None
            else:
                if output:
                    self.buffer += output
                    log.msg('Got output: %s'%(len(self.buffer)))
                else:
                    # reached end of file...
                    break
        if self.buffer:
            lines = self.buffer.splitlines()
            if not self.buffer.endswith( '\n' ):
                self.buffer = lines.pop()
            else:
                self.buffer = ''
            return lines
        return []

def test_consumer( lines ):
    for line in lines:
        log.msg('line: %r'%(line,))

def main():
    log.startLogging(sys.stderr)
    FileTail( sys.argv[1], test_consumer ).start_watching()
    reactor.run()

if __name__ == "__main__":
    main()
    
