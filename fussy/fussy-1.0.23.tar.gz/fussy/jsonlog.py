"""JSONLogServer client for Python logging

To install a JSON Log Server client (logger), do the following::

    from fussy.jsonlog import JSONSocketHandler
    
    root = logging.getLogger( '' )
    handler = JSONSocketHandler( )
    # important, the logger is *not* intended for high volumes of 
    # messages, it is intended for messages you might actually want to 
    # look at, so set the level high!
    handler.setLevel( logging.WARN )
    root.addHandler( handler )

To add to a Django logging config::

    'handlers': {
        'json': {
            'level': 'WARN',
            'class': 'fussy.jsonlog.JSONSocketHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['json'],
        }
    }

Records stored look like this:

    {
      "name": "root", # logger name
      "created": 1354250362.095767, # unix timestamp (time.time())
      "args": [], # unicode(a) for a in args
      "module": "<stdin>", # python module from which the message comes
      "funcName": "<module>", # function from which the message was generated
      "levelno": 30, # numeric code for the level
      "pathname": "<stdin>", # path to the file/module
      "lineno": 1, # line at which the logging message is produced
      "msg": "Hello world", # message, with *no* substitutions performed!
      "filename": "<stdin>", # the file name for the code generating the error
      "levelname": "WARNING" # the textual name of the level
    }
    
    
"""
import logging 
import logging.handlers
import socket
import json
import time
import traceback
import threading
LOGGING_PORT = 2514
try:
    unicode 
except NameError:
    unicode = str

def as_bytes(content):
    if isinstance(content,unicode):
        return content.encode('utf-8')
    return content

class JSONSocketHandler( logging.handlers.SocketHandler ):
    """Handler which sends JSON-formatted subsets of logging records to a socket
    
    The handler actually uses a JSONFormatter to format the records, 
    and you can override the formatter by doing a ``setFormatter`` on the 
    handler, should you wish to override the format logged.
    
    Note that messages *must* be single-line, as the log server uses newlines 
    as the indication that a record may be written (so if you aren't single line 
    your messages can become scrambled).
    """
    def __init__( self, host='127.0.0.1',port=LOGGING_PORT ):
        logging.handlers.SocketHandler.__init__( self, host, port )
        if not self.formatter:
            self.formatter = JSONFormatter()
        # we really, really, really want to get messages through, and 
        # the log server should *always* be up, so be far more aggressive 
        # about retrying to send messages...
        self.retryStart = .01
        self.retryMax = 5.0
        self.retryFactor = 2.0
        self.buffer = []
        self.lock = threading.RLock()
        
    def makePickle( self, record ):
        """We don't want to pickle, we want to jsonify"""
        return self.formatter.format( record )
    MAX_BUFFER = 100
    def send(self, s):
        """Send our content to the other side
        
        This implementation stores any unsent messages locally until we can 
        get to the server...
        """
        self.buffer.append( s )
        if len(self.buffer) > self.MAX_BUFFER:
            self.buffer = self.buffer[-self.MAX_BUFFER:]
        if self.sock is None:
            self.createSocket()
        if self.sock:
            while self.buffer:
                try:
                    s = self.buffer.pop(0)
                except IndexError:
                    break
                else:
                    try:
                        sentsofar = 0
                        left = len(s)
                        while left > 0:
                            sent = self.sock.send(s[sentsofar:])
                            sentsofar = sentsofar + sent
                            left = left - sent
                    except socket.error:
                        # s was not sent in full, so re-schedule...
                        self.buffer.insert(0,s)
                        self.sock.close()
                        self.sock = None  # so we can call createSocket next time

class JSONFormatter( logging.Formatter ):
    suppress = set([
        'relativeCreated','process','threadName','thread','msecs','processName',
        'exc_info','exc_text','args','message','request',
    ])
    MSG_FORMATTER = logging.Formatter()
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    def format( self, record ):
        """Format the record as a subset of fields in JSON notation
        
        self.MSG_FORMATTER is applied to the record to produce "msg", so that 
        records do not need args to be transmitted
        
        Each field in self.suppress is removed from the records (mostly to 
        reduce record size).
        
        If traceback.format_exc() returns something other than ``'None\n'`` then 
        the traceback is added to the record as 'traceback' key
        
        The JSON is generated with sort_keys, so the format should be fairly 
        consistent in the final file.
        """
        raw = record.__dict__.copy()
        # Do a basic message format...
        try:
            raw['msg'] = self.MSG_FORMATTER.format( record )
        except Exception:
            raw['msg'] = 'Unable to format message'
            pass
        
        if raw['levelno'] >= logging.WARNING:
            trace = traceback.format_exc()
            if trace and trace != 'None\n':
                raw['traceback'] = trace
        raw['created_formatted'] = time.strftime(
            self.DATE_FORMAT,
            time.localtime(raw['created'])
        )
        for key in self.suppress:
            if key in raw:
                del raw[key]
        return as_bytes(
            json.dumps( raw, sort_keys=True, skipkeys=True, separators=(',', ':') )
         ) + b'\n'

def sample_log():
    handler = JSONSocketHandler( )
    handler.setLevel(logging.WARNING)
    log = logging.getLogger( 'blue' )
    log.addHandler( handler )
    log.propagate = False
    log.info( 'Should not show up' )
    log.warning( 'Regular log should show up: %s', 'this' )
    try:
        raise AttributeError( 'blue' )
    except Exception:
        log.error( 'Hello world: %s', 'this' )
        print('done')
    handler.close()
    
if __name__ == '__main__':
    sample_log()
