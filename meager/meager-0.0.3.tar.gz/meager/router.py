import re
class Router(object):
    def __init__(self):
        self.routes = []

    def create_route_expression(self, route):
        expression = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        return re.compile(f"^{expression}$")

    def register_route(self, url, func, server_options):
        pattern = self.create_route_expression(url)
        self.routes.append((pattern, func, server_options))

    def route(self, url, server_options={}, **options):
        def decorator(func):
            self.register_route(url, func, server_options)
            return func
        return decorator

    def match_request(self, url):
        for routexp, func, server_options in self.routes:
            m = routexp.match(url)
            if(m):
                return m.groupdict(), func, server_options
        return None