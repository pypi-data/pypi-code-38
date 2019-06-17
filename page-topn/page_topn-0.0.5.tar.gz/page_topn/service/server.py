import tornado.ioloop
import tornado.httpserver
from page_topn.service.configs import options
from page_topn.service.applications import Applications
import sys
import os
# print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(dir_name)

def start():
    app = Applications()
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.bind(options.get("port"))
    httpServer.start(1)

    tornado.ioloop.IOLoop.current().start()



if __name__ =="__main__":
    start()