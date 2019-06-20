from http_server_base.logged_request_handler import Logged_RequestHandler

class Empty_RequestHandler(Logged_RequestHandler):
    
    logger_name = 'http_server.empty_handler'
    redirect_page = None

    def initialize(self, redirect_page, **kwargs):
        super().initialize(**kwargs)
        self.redirect_page = redirect_page

    def get(self, *args, **kwargs):
        self.redirect(self.redirect_page)