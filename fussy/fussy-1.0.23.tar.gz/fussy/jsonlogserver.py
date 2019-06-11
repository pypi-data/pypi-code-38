"""JSON log server (log-line server)

Logs each incoming log line to the disk *without modification*, but 
only writes lines when the line is complete, so allows you to log from 
many processes simultaneously.

See :py:class:`fussy.jsonlog.JSONSocketHandler` for how to send messages 
to the log server.

The log server should be set up to run under a process manager 
(e.g. supervisord) like so::

    [program:fussylog]
    command=/opt/firmware/current/env/bin/fussy-log-server -f /var/www/logs/errors.json
    autorestart=true
    user=<someuser>
    directory=/var/www/logs
    stopasgroup=true
    killasgroup=true 
    startretries=200
    priority=50
"""
import asyncore
import socket
import json
import os 
import sys
import time
import logging,traceback
log = logging.getLogger( __name__ )
from optparse import OptionParser

class LogHandler(asyncore.dispatcher):
    """Handle messages from a single client process"""
    buffer = ''
    def __init__( self, *args, **named ):
        self.sink = named.pop( 'sink' )
        asyncore.dispatcher.__init__( self, *args, **named )
    def handle_read(self):
        try:
            self.buffer += self.recv(8192)
            i = 0
            while '\n' in self.buffer and i < 50:
                index = self.buffer.index( '\n' )
                record,self.buffer = self.buffer[:index+1],self.buffer[index+1:]
                self.sink( record )
                i += 1
            if i >= 50:
                log.warning( "More than 50 records received at the same time!" )
        except Exception:
            log.error( "Unhandled error on read: %s", traceback.format_exc() )
            self.close()
            raise
    def handle_close(self):
        self.close()
    def writable( self ):
        return False

class LogServer(asyncore.dispatcher):
    """Handle incoming connections from however many processes wish to log"""
    def __init__(self, host='127.0.0.1', port=2514, sink=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.sink = sink
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        try:
            pair = self.accept()
            if pair is None:
                pass
            else:
                sock, addr = pair
                log.info( "New connection from: %s", addr )
                LogHandler(sock, sink=self.sink)
        except Exception:
            log.error( "Unhandled error on accept: %s", traceback.format_exc())
            raise

ROTATION = 1024*1024
ROTATION_COUNT = 5
class Sink( object ):
    """Location to which to send messages (rotating files in the simple case)
    """
    file_handle = None
    def __init__( self, filename, max_bytes = ROTATION, max_rotation=ROTATION_COUNT ):
        """Create a sink for the given filename"""
        self.filename = filename 
        self.max_bytes = max_bytes
        self.max_rotation = max_rotation
        if os.path.exists( self.filename ):
            self.written = self.last_flush = os.stat( self.filename ).st_size
            self.file_handle = open( self.filename, 'ab' )
        else:
            self.written = 0
            self.last_flush = 0
            self.file_handle = open( self.filename, 'wb' )
        self.file_handle.write(b'\n')
        self.written += 1
        #self.rotate()
    def rotate( self ):
        log.info( 'Rotating: %s', self.filename )
        if self.file_handle:
            self.file_handle.close()
        self.written = 0
        self.last_flush = 0
        if os.path.exists( self.filename ):
            for i in range( self.max_rotation-1, 0, -1 ): # stop at 1
                rot = '%s.%s'%( self.filename, i )
                rotpone = '%s.%s'%( self.filename, i+1 )
                if os.path.exists( rot ) and os.stat( rot ).st_size > 0:
                    os.rename( rot, rotpone )
            i = 1
            rot = '%s.%s'%( self.filename, i )
            os.rename( self.filename, rot )
        self.file_handle = open( self.filename, 'wb' )
    # By default, flush on every write, not good on a laptop, but we're logging 
    # high-priority messages with this thing...
    FLUSH_SIZE = 0
    def __call__( self, record ):
        self.written += len(record)
        if self.written > self.max_bytes:
            self.rotate()
            self.written = len(record)
        self.file_handle.write( record )
        if self.written - self.last_flush > self.FLUSH_SIZE:
            self.file_handle.flush()
            self.last_flush = self.written

LOGGING_PORT = 2514
def server_options():
    parser = OptionParser()
    parser.add_option(
        '-f','--file',
        dest = 'filename',
        default = '/tmp/json.log',
        help="File into which to log",
    )
    parser.add_option(
        '-r', '--rotation',
        dest = 'rotation',
        default = ROTATION,
        help = "Size after which to rotate log file (bytes), defaults %s"%( ROTATION,),
    )
    parser.add_option(
        '-c', '--count',
        dest = 'rotation_count',
        default = ROTATION_COUNT,
        help = "Number of rotated logs to retain, default %s"%( ROTATION_COUNT, ),
    )
    parser.add_option(
        '-p', '--port',
        dest = 'port',
        default = 2514,
        type = 'int',
        help = 'Port on which to listen',
    )
    return parser

def main():
    """Sink json-formatted messages into a rotating file handle"""
    parser = server_options()
    options,args = parser.parse_args()
    directory = os.path.dirname( options.filename )
    if not os.path.exists( directory ):
        os.makedirs( directory )
    logging.basicConfig( 
        filename=options.filename + '.logserver.log', level=logging.INFO 
    )
    sink = Sink( 
        filename=options.filename, 
        max_bytes=options.rotation, 
        max_rotation=options.rotation_count,
    )
    log.info( 'Listening on port %s and writing to file %s', options.port, options.filename )
    LogServer( sink = sink, port=options.port )
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        return 0

def format_date( ts ):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
def format_record( record ):
    record['date'] = format_date(record['created'])
    record['message'] = '   '.join( record['msg'].splitlines())
    return u'%(date)s %(levelname)s %(name)s: (%(filename)s:%(lineno)s %(funcName)s)    %(message)s'%record
def format_log(filename):
    """Format a given fussy log server file into more traditional format"""
    for line in open( filename ):
        try:
            if line.strip():
                print(( format_record( json.loads(line.strip())).encode('utf-8')))
        except Exception:
            log.warning('Failed to process line: %r',  line)
def format_log_main():
    if sys.argv[1:]:
        for filename in sys.argv[1:]:
            format_log( filename )
        return 0
    else:
        print( 'fussy-format-log filename [filename...]' )
        return 1
    
if __name__ == "__main__":
    main()
