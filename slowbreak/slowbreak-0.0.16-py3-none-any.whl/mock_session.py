from .app import BaseApp

class MockSessionApp(BaseApp):
    
    def __init__(self, msgs_in=[], *args, **kwargs):
        
        self.sent_messages = []
        
        super(MockSessionApp, self).__init__(*args, **kwargs)
        
        for m in msgs_in:
            self.msg_in(m)
            
    def on_send_request(self, message):
        self.sent_messages.append(message)
        
        return None # No more processing going down.
    
    def msg_in(self, message):
        self.upper_app._on_msg_in(message)
    
    def clear_sent_messages(self):
        self.sent_messages[:] = []