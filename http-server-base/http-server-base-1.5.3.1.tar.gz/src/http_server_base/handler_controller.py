from typing import List, Tuple, Type, Pattern, Any, Dict, Union

from tornado.web import RequestHandler, Application

HandlerType = Union[Tuple[Pattern[str], Type[RequestHandler]], Tuple[Pattern[str], Type[RequestHandler], Dict[str, Any]]]
HandlerListType = List[HandlerType]

class HandlerController:
    base_path: str
    application: Application = None
    
    handlers: HandlerListType = list()
    
    def __init__(self, application: Application):
        self.application = application
    
    def get_self_handlers(self) -> HandlerListType:
        return self.handlers
