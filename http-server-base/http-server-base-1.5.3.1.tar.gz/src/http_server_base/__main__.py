import io
import logging
from logging import StreamHandler
from typing import List, Iterable

from http_server_base import ApplicationBase, BasicResponder, TextBasicResponder, JsonBasicResponder, Logged_RequestHandler, HtmlBasicResponder

class EchoHandler(Logged_RequestHandler):
    logger_name = 'echo_server.handler'
    def get(self, *args, **kwargs):
        _logger = logging.getLogger(self.logger_name)
        _str_io = io.StringIO()
        _handler = StreamHandler(_str_io)
        _logger.addHandler(_handler)
        self.dump_request(self.request, dump_body=True)
        _content = _str_io.getvalue()
        self.resp_success(200, message=f'<h3>Server: {self.application.name}</h3>', result=f'<pre>{_content}</pre>')

class EchoServer(ApplicationBase):
    logger_name = 'echo_server'
    responder_class = HtmlBasicResponder
    handlers = [ ('.*', EchoHandler) ]

def parse_args(argv: Iterable[str]):
    args = dict()
    responders = dict(basic=BasicResponder, html=HtmlBasicResponder, text=TextBasicResponder, json=JsonBasicResponder)
    server = ApplicationBase
    for _arg in argv:
        
        _arg_name, _sep, _arg_value = _arg.partition('=')
        if (_sep):
            if (_arg_name == 'responder'):
                if (_arg_value in responders):
                    args['responder_class'] = responders[_arg]
                    continue
            
            args[_arg_name] = _arg_value
        
        if (_arg == 'echo'):
            server = EchoServer
            continue
        
        try:
            args['listen_port'] = int(_arg)
        except (ValueError, IndexError):
            pass
    
    return server, args

if (__name__ == '__main__'):
    import sys
    
    server, args = parse_args(sys.argv[1:])
    server.simple_start_server(**args)
