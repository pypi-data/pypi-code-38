from http_server_base.logged_request_handler import Logged_RequestHandler

class HealthCheck_RequestHandler(Logged_RequestHandler):
    """
    Requests 200: HealthCheckResponse to ANY incoming GET request.
    """
    
    logger_name = 'http_server.healthcheck'

    def get(self, *args, **kwargs):
        self.resp_success(200)

        self.add_header('Content-type', 'text/html')
        message = "HealthCheckResponse"
        self.write(bytes(message, "utf8"))
        return
