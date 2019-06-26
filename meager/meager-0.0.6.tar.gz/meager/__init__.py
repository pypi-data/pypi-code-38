import meager.router
import meager.http
import meager.logger
import json
import socketserver

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).decode("utf-8")
        meager.logger.log(__class__, f"Got request from {self.client_address[0]}")
        parsed = meager.http.parse(self.data)
        route_match = self.server._router.match_request(parsed["url"])
        response = {
            "status": "OK 200",
            "http-version": "HTTP/1.1",
            "content-type": "text/html"
            }

        if(route_match):
            kwargs, function, server_options = route_match
            for key, value in server_options.items():
                response[key] = value
            response["content"] = function({"post": kwargs, "ip": self.client_address[0],"request": parsed})
            self.request.sendall(meager.http.build_response(response).encode("utf-8"))
        else:
            self.request.sendall(b"HTTP/1.1 OK 404\r\nContent-Type: text/html\r\n\r\n<h1>404 not found</h1>")

class Server(object):
    def __init__(self, port=2920, host="127.0.0.1"):
        self.port = port
        self.host = host
        self.router = meager.router.Router()

    def serve(self):
        with socketserver.TCPServer((self.host, self.port), RequestHandler) as sockserv:
            sockserv._router = self.router
            sockserv.serve_forever()
