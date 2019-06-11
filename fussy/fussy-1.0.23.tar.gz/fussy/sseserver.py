"""Server Sent Events Channel for Fussy

This is a push service that is intended for use in very small
servers (such as fussy is normally used to manage). It does 
*not* attempt to scale up to huge installations.

Based on this code:

    https://github.com/juggernaut/twisted-sse-demo

Example usage (Note: you may need a shim to get this to work in all browsers,
such as: https://github.com/Yaffle/EventSource ):

    var eventSource = new EventSource("http://localhost:12000/test2.txt");
    eventSource.addEventListener('test2.txt',function(event) {
        element = $(".moo-test");
        element.text(event.type+' '+event.lastEventId+' '+event.data);
    });

Now to send an event:

    echo "Moo" > /var/firmware/protected/test2.txt

and the event will be formatted into the web-page

Nginx stanza to include the server:

    location /__sse__/ {
        # Protected by the web app, but served by the server...
        internal;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Nginx-Hosted "Yes";
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Protocol $scheme;
        proxy_read_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_redirect off;
        
        proxy_pass http://localhost:12000/;
        break;
    }
    
Then in Django (web/app) you do an NGINX Redirect *after*
you have decided that a given user is allowed to view *all* 
channels in the sse_server:

    @permission_required('yada.yoo')
    def foo( request, interest ):
        # validate rights to get to the these channels
        if not channel_permissions( interest ):
            return HttpResponse( 'Permissions prevent listening to those channels', 401)
        if request.META.get( 'HTTP_X_NGINX_HOSTED' ):
            response = HttpResponse( '' )
            response['X-Accel-Redirect'] = '/__sse__/%s'%(urllib.quote_plus(interest))
            return response
        else:
            return HttpResponseRedirect( '%s/%s'%(settings.SSE_SERVER_DEBUG_LOCATION,%(urllib.quote_plus(interest) )

Clients can then connect and process the SSEvents at whatever URL 
you have put the bit of view code there.
"""
import re, sys, urllib, weakref
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from twisted.internet import inotify
from twisted.python import filepath
from twisted.internet import task
from twisted.internet import endpoints
from fussy import tailprotocol

PUBLISHABLE = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9-.*]{0,64})|[*]$')
DEFAULT_PUBLISH_ROOT = '/var/firmware/protected/live'
DEFAULT_ENDPOINT = 'tcp:12000:interface=127.0.0.1'
DEFAULT_KEEPALIVE = 20.0

class RootMonitor( object ):
    def __init__(self,root, server):
        self.root = root 
        self.server = server
        self.server.monitor = self
        self.start_watching()
    def start_watching(self):
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(
            filepath.FilePath(self.root), 
            mask = inotify.IN_CLOSE_WRITE|inotify.IN_MOVED_TO|inotify.IN_MODIFY,
            callbacks=[self.on_file_change]
        )
    @classmethod
    def publishable(cls, name ):
        return bool(PUBLISHABLE.match(name))
    
    def on_file_change(self,ignored, filepath, mask):
        """A file has changed, see if it's a publishable event"""
        base = filepath.basename()
        log.msg('Update to %s'%(base,))
        if self.publishable( base ):
            if mask & inotify.IN_MODIFY:
                # tail operations only...
                self.server.update_tails( filepath )
            else:
#                if mask & inotify.IN_CLOSE_WRITE:
#                    self.server.close_tails( filepath )
                try:
                    content = filepath.open().read().splitlines()
                except Exception:
                    log.msg("Unable to read %s"%(filepath,))
                else:
                    self.server.send_all( base, content )
    def current(self):
        """Return the current paths/events known to the server"""
        root = filepath.FilePath(self.root)
        return sorted(root.globChildren('*'), key=lambda x: x.getModificationTime())

class SSEServer(resource.Resource):
    """SSE Server that publishes files from a directory"""
    isLeaf = True
    def __init__(self, keepalive=DEFAULT_KEEPALIVE):
        self.subscribers = {}
        self.tails = {}
        self.event_id = 1
        self.keepalive = keepalive
        task.LoopingCall( self.on_keepalive ).start( self.keepalive )
    _monitor = None
    @property
    def monitor(self):
        return self._monitor()
    @monitor.setter
    def monitor(self, other):
        self._monitor = weakref.ref(other)
    
    def on_keepalive(self):
        """Send a keepalive (ping) message"""
        for subscriber,interests in self.subscribers.items():
            try:
                subscriber.write(":\n")
            except Exception:
                pass
        
    def send_all(self, event, content, subscribers=None ):
        log.msg("Sending event: %r"%(event,))
        if not self.subscribers:
            # don't waste ids...
            log.msg("No current subscribers")
            return
        subscribers = [
            (s,i) for s,i in (subscribers or self.subscribers).items()
            if self.interested( event, i )
        ]
        if not subscribers:
            log.msg("No one interested in %s"%(event,))
            return
        self.event_id += 1
        self.event_id %= 0xffffff
        for subscriber,interests in subscribers:
            log.msg('Sending %s lines to %s'%(len(content),subscriber,))
            try:
                if interests:
                    subscriber.write("event: %s\n"%(event,))
                subscriber.write("id: %s\n"%(self.event_id,))
                for line in content:
                    subscriber.write("data: %s\n" % line)
                # NOTE: the last CRLF is required to dispatch the event at the client
                subscriber.write("\n")
            except Exception as err:
                log.msg( "Failed sending to %s: %s"%( subscriber, err) )

    def interested(self, base, interests ):
        """Is this set of interests interested in base event?"""
        if (not interests) or '*' in interests:
            # interested in everything...
            return True 
        else:
            return base in interests
    def update_tails(self, filepath ):
        """Update any items which are tailing filepath.basename"""
        base = filepath.basename()
        for subscriber in self.subscribers.keys():
            map = getattr(subscriber,'tails',{})
            log.msg("tails: %s"%(map))
            if base in map:
                tail = map.get(filepath)
                if tail is None:
                    log.msg( 'Starting new tail for %s'%(filepath.path))
                    tail = map[filepath] = tailprotocol.FileTail( filepath )
                lines = tail.read_from_file()
                if lines:
                    self.send_all( base, lines, {subscriber:{base:True}} )
    def render_GET(self, request):
        for header,value in [
            ('Content-Type', 'text/event-stream; charset=utf-8'),
            ('Access-Control-Allow-Origin','*'),
            ('Connection','keep-alive'),
            ("Cache-Control", "no-cache"),
        ]:
            request.setHeader(header,value)
        request.setResponseCode(200)
        log.msg( "Connection from %s"%(request.getClientIP()))
        d = request.notifyFinish()
        d.addBoth(self.on_disconnect)
        self.subscribers[request] = interests = set()
        for fragment in request.postpath:
            fragment = urllib.unquote_plus(fragment)
            for interest in fragment.split(' '):
                if interest.startswith('-'):
                    interest = interest[1:]
                    if RootMonitor.publishable(interest):
                        if not getattr(request,'tails',None):
                            request.tails = {}
                        # set of tails for the interest (indexed by path)
                        request.tails.setdefault( interest, {} )
                if RootMonitor.publishable( interest ):
                    interests.add(interest)
        request.write("")
        reactor.callLater(0, self.send_initial, request )
        return server.NOT_DONE_YET
    def send_initial(self, subscriber ):
        interests = self.subscribers[subscriber]
        # do *initial* sends for each of the interests...
        for existing in self.monitor.current():
            base = existing.basename()
            if self.interested( base, interests ):
                try:
                    content = existing.open().read().splitlines()
                except Exception:
                    log.msg("Unable to read %s"%(existing,))
                else:
                    self.send_all( base, content, {subscriber:interests} )
#            elif base in self.logs and subscriber in self.logs[base]:
#                size = existing.getsize()
#                content = existing.open().read( size )
#                lines = content.splitlines()
#                if lines and lines[-1] == '':
#                    lines = lines[:1]
#                else:
#                    size = size-len(lines[-1])
#                    lines = lines[:-1]
#                self.send_all( base, lines, {subscriber:

    def on_disconnect(self, subscriber):
        log.msg('Disconnect: %s'%(subscriber))
        if subscriber in self.subscribers:
            if not subscriber.finished:
                subscriber.finish()
            log.msg("Removing subscriber..")
            try:
                del self.subscribers[ subscriber ]  
            except KeyError:
                log.info("Unable to remove %s"%(subscriber,))
            for name, interested in self.logs.items():
                if subscriber in interested:
                    del interested[subscriber]
                if not interested:
                    del self.logs[name]
    
def get_options():
    import argparse
    parser = argparse.ArgumentParser(description='Run SSE server (Twisted Inotify Publishing Channels)')
    parser.add_argument(
        '-r','--root', metavar='DIR',
        default = DEFAULT_PUBLISH_ROOT,
        help="Directory to be published, default: %s"%(DEFAULT_PUBLISH_ROOT,),
    )
    parser.add_argument(
        '-e','--endpoint', metavar='ENDPOINT',
        default = DEFAULT_ENDPOINT,
        help="Twisted-style endpoint on which to publish, default: %s\nSee: http://twistedmatrix.com/documents/current/api/twisted.internet.endpoints.serverFromString.html"%(DEFAULT_ENDPOINT,),
    )
    parser.add_argument(
        '-k','--keepalive',metavar='SECONDS',
        default=DEFAULT_KEEPALIVE,
        help="Period at which keepalive messages will be sent",
    )
    parser.add_argument(
        '-l','--logfile',metavar='FILE',
        default = None,
        help="Log file to write, default: stdout",
    )
    return parser

def main():
    options = get_options().parse_args()
    if options.logfile:
        log_target = open(options.logfile,'w')
    else:
        log_target = sys.stdout
    log.startLogging(log_target)
    log.msg( "Publishing %s on %s"%(
        options.root,
        options.endpoint,
    ))
    sse = SSEServer( keepalive = options.keepalive )
    root = RootMonitor( options.root, sse )
    assert root
    site = server.Site(sse)
    endpoint = endpoints.serverFromString(reactor,options.endpoint )
    endpoint.listen(site)
    reactor.run()

if __name__ == "__main__":
    main()
