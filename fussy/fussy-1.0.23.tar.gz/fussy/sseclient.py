"""SSE Client implementation

Needs:

* Reconnecting Client 
* Callback to run on each event
* Default callback should be to mirror the events locally

  * write each (publishable) event to a target/mirror directory (with twrite)

Based on:

    https://github.com/juggernaut/twisted-sse-demo
"""
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import ssl
import logging,json
try:
    import urlparse 
except ImportError:
    from urllib import parse as urlparse
log = logging.getLogger(__name__)
DEFAULT_URL = 'http://localhost:12000/'

class SSEClientProtocol(LineReceiver):
    def __init__(self):
        self.event = 'message'
        self.data = ''
        self.headers = True
        self.status_code = None
    def connectionMade(self):
        self.transport.write( self.request_headers() )
        
    def request_headers(self):
        return 'GET %s HTTP/1.1\r\n%s\r\n\r\n'%(
            self.factory.final_url(),
            '\r\n'.join([
                '%s: %s'%(k,v) for k,v in [
                    ('Connection','keep-alive'),
                    ('Accept','text/event-stream'),
                    #Last-Event-ID
                ] + self.factory.headers.items()
            ]),
        )

    def lineReceived(self, line):
        """Process a single incoming line"""
        if line.strip() == '':
            if self.headers:
                self.headers = False
            else:
                self.dispatchEvent()
        if self.headers:
            if not self.status_code and line.startswith('HTTP/'):
                self.status_code = int(line.strip().split()[1])
                if self.status_code in (302,401):
                    self.factory.login_first()
            log.info('H: %s',line)
        else:
            #log.info("P: %s",line)
            try:
                field, value = line.split(':', 1)
                # If value starts with a space, strip it.
                value = lstrip(value)
            except ValueError:
                # We got a line with no colon, treat it as a field(ignore)
                return

            if field == '':
                # This is a comment; ignore
                pass
            elif field == 'data':
                self.data += value + '\n'
            elif field == 'event':
                self.event = value.strip()
            elif field == 'id':
                # Not implemented
                self.id = value.strip()
            elif field == 'retry':
                # Not implemented
                # should modify our transport's connection parameters...
                self.transport.initialDelay = float(value.strip())

    def dispatchEvent(self):
        """Dispatch the event"""
        # If last character is LF, strip it.
        if self.data.endswith('\n'):
            self.data = self.data[:-1]
        self.factory.dispatchEvent( self.event, self.data )
        self.data = ''
        self.event = 'message'

class SSEClientFactory(protocol.ReconnectingClientFactory):
    """Reconnecting client that generates SSEClient instances"""
    factor = 1.1
    initialDelay = 1.0
    maxDelay = 20.0
    protocol = SSEClientProtocol
    def __init__(self,*args,**named):
        if 'url' in named:
            self.url = named.pop('url')
        else:
            self.url = DEFAULT_URL
        if 'callbacks' in named:
            self.callbacks = named.pop('callbacks')
        else:
            self.callbacks = {}
        if 'interests' in named:
            self.interests = named.pop('interests')
        else:
            self.interests = '*'
        self.headers = {
            'keep-alive': 3600,
        }
        self.headers.update( named )
    def buildProtocol(self, addr):
        self.resetDelay()
        protocol = SSEClientProtocol()
        protocol.factory = self 
        return protocol
    
    def dispatchEvent(self, event='message', data=''):
        """Dispatch event to one of our handlers if the event is registered"""
        if event in self.callbacks:
            callback = self.callbacks.get(event)
        elif None in self.callbacks:
            callback = self.callbacks.get(None)
        else:
            return 
        try:
            callback( event, data )
        except Exception:
            log.exception("Failure processing %r:%r with function %s",event,data,callback)
    def setFinishedDeferred(self, d):
        self.finished = d
    def addCallback(self, event, func):
        self.callbacks[event] = func
    
    def final_url(self):
        base = self.url 
        if not base.endswith('/'):
            base += '/'
        return base + self.interests

def lstrip(value):
    return value[1:] if value.startswith(' ') else value

def debug_callback(event,data):
    try:
        record = json.loads(data)
    except Exception:
        #log.exception("Failure parsing %r data %r",event,data)
        log.info("%s: %r",event,data)
    else:
        log.info("%s: %s",event,record)

class NoverifyFactory(ssl.ClientContextFactory):
    def getContext(self):
        from OpenSSL import SSL
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.verify = False
        return ctx


def client( url, callbacks=None ):
    if not callbacks:
        callbacks = { 
            None:debug_callback,
        }
    parsed = urlparse.urlparse(url)
    factory = SSEClientFactory( callbacks=callbacks, url=parsed.path, host=parsed.hostname )
    if parsed.scheme == 'httpsu':
        reactor.connectSSL(parsed.hostname,parsed.port or 443,factory,NoverifyFactory())
    elif parsed.scheme == 'https':
        reactor.connectSSL(parsed.hostname,parsed.port or 443,factory)
    elif parsed.scheme == 'http':
        reactor.connectTCP(parsed.hostname,parsed.port or 80,factory)
    return factory

def get_options():
    import argparse
    parser = argparse.ArgumentParser(description='Run SSE client demo (Twisted Inotify Publishing Channels)')
    parser.add_argument(
        '-u','--url', metavar='URL',
        default = DEFAULT_URL,
        help="http url to which to connect to the server, default: %s"%(DEFAULT_URL,),
    )
    
    return parser

def main():
    logging.basicConfig(level=logging.INFO)
    options = get_options().parse_args()
    factory = client( options.url )
    assert factory
    reactor.run()

if __name__ == "__main__":
    main()
