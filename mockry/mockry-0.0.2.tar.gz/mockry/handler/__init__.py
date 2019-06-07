from tort.handler import RequestHandler


class PageHandler(RequestHandler):
    def compute_etag(self):
        return None

    def check_xsrf_cookie(self):
        pass
