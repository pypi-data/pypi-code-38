from .session import thread_fun
from .app import BaseApp
from .message import Message
from .constants import MsgType, Tag

import logging
import threading

LOG = logging.getLogger(__name__)
LOG_IN = LOG.getChild("in")
LOG_OUT = LOG.getChild("out")

class BarebonesSessionApp(BaseApp):
    """\
Do nothing session. To be used in weird and arbitrary homologations

It connects just once, has a single thread (in thread) and the current thread is the output thread.
All the received messages are sent to the upper app (if exist) and logged.
Output is thread-unsafe and no header nor any kind of transactional features are implemented. 

Do not use in production at all. 
"""
    
    class InThread(threading.Thread): 
        def __init__(self, app):
            super(BarebonesSessionApp.InThread, self).__init__()
            self.app = app
            
        @thread_fun      
        def run(self):
            try:
                messages = Message.from_socket(self.app.socket)
                for message in messages:
                    try:
                        LOG_IN.info("Received %r" % message)
                        if message is None:
                            LOG.warning("Timeout while waiting for message")
                        else:
                            self.app._on_msg_in(message)
                            
                            if MsgType.Logout == message.get_field(Tag.MsgType):
                                LOG.info("Received logout. Stopping thread")
                                return
                    except Exception as e:
                        LOG.warning("Ignoring exception %s while processing message %r" % (e, message), exc_info=True)
                raise Exception("Connection closed without logout")
            except Exception as e:
                LOG.exception("Unhandled exception %s" %e)
    
    def __init__(self,
        socket, 
        *args, 
        **kwargs
    ):
        super(BarebonesSessionApp, self).__init__(*args, **kwargs)
        self.socket = socket
        
        self.InThread(app=self).start()
        
    def on_send_request(self, message):
        LOG_OUT.info("Sending %r" % message)
        self.socket.sendall(message.to_buf())
        return None

        
