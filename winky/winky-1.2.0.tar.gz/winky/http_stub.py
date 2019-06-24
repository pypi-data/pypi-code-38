from winky.http_message import HTTPMessage
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from time import sleep
import ssl


class HTTPStub:

    def __init__(self, logic, port, ssl=None):
        self.__logic = logic
        self.__port = port
        self.__ssl = ssl
        self.__payment_init_server = None
        self.__stub_request_list = []
        self.__stub_response_list = []
        self.__shutdown_flag = False
        self.__thread = None

    def __shutdown(self):
        return self.__shutdown_flag


    def __http_processor(self, logic, stub_request_list, stub_response_list, think_time, shutdown):
        class __HttpProcessor(BaseHTTPRequestHandler):

            def do_POST(self):
                buf = think_time
                while buf > 0:
                    buf = buf - 0.1
                    sleep(0.1)
                    if shutdown():
                        return
                try:
                    input_message = HTTPMessage()
                    output_message = HTTPMessage()

                    if self.headers['Content-Length']:
                        content_length = int(self.headers['Content-Length'])
                        input_message.body = self.rfile.read(content_length).decode()
                    input_message.headers = self.headers
                    input_message.headers['_mock_path'] = str(self.path)

                    stub_request_list.append(input_message)
                    logic(input_message, output_message)
                    stub_response_list.append(output_message)

                    self.send_response(output_message.code)
                    for header in output_message.headers.items():
                        self.send_header(header[0], header[1])
                    self.end_headers()
                    self.wfile.write(output_message.body.encode())

                except Exception as ex:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(ex.args[0]).encode())

            def do_GET(self):
                self.do_POST()

            def log_message(self, format, *args):
               pass

        return __HttpProcessor

    class __ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        pass

    def __start_server(self):
        self.__payment_init_server = self.__ThreadedHTTPServer(('', self.__port), self.__http_processor(self.__logic,
                                                                                                       self.__stub_request_list,
                                                                                                       self.__stub_response_list,
                                                                                                       self.__think_time,
                                                                                                       self.__shutdown))
        if self.__ssl:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.__ssl.cert, keyfile=self.__ssl.key)
            if self.__ssl.cacert:
                context.verify_mode = ssl.CERT_REQUIRED
                context.load_verify_locations(cafile=self.__ssl.cacert)
            self.__payment_init_server.socket = context.wrap_socket(self.__payment_init_server.socket,
                                                                        server_side=True)

        self.__payment_init_server.serve_forever()

    def run(self, think_time=0):
        self.__think_time = think_time
        self.__thread = threading.Thread(target=self.__start_server)
        self.__thread.daemon = True
        self.__thread.start()
        sleep(0.1)

    def stop(self, think_time = 0.1):
        sleep(think_time)
        if self.__thread:
            self.__payment_init_server.server_close()
            self.__payment_init_server.shutdown()
            self.__shutdown_flag = True
            self.__stub_request_list.clear()
            self.__stub_response_list.clear()

    def get_stub_request(self, index):
        return self.__stub_history(index, self.__stub_request_list)

    def get_stub_response(self, index):
        return self.__stub_history(index, self.__stub_response_list)

    def __stub_history(self, index, list):
        # if not index:
        #     index = len(self.__stub_response_list) - 1
        for i in range(100):
            if len(list) - 1 >= index:
                break
            sleep(0.1)

        if not index < len(list):
            raise IndexError(f'Count of items in the list = {len(list)}')
        return list[index]


    @property
    def request_count(self):
        return len(self.__stub_request_list)
