class RouteInfo(object):
    def __init__(self,
                 route_url,
                 route_method,
                 route_target,
                 route_id):
        self.route_url = route_url
        self.route_method = route_method
        self.route_target = route_target
        self.route_id = route_id
