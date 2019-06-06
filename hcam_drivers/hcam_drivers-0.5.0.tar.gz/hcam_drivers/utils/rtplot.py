from __future__ import print_function, unicode_literals, absolute_import, division
from six.moves import socketserver
try:
    from http.server import BaseHTTPRequestHandler
except:
    from BaseHTTPServer import BaseHTTPRequestHandler
import socket
import errno

from hcam_widgets import DriverError


class RtplotHandler(BaseHTTPRequestHandler):
    """
    Handler for requests from rtplot. It accesses the window
    parameters via the 'server' attribute; the Server class
    that comes next stores these in on instantiation.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        wins = self.server.instpars.getRtplotWins()
        if wins == '':
            self.wfile.write('No valid data available\r\n'.encode())
        else:
            self.wfile.write(wins.encode())


class RtplotServer(socketserver.TCPServer):
    """
    Server for requests from rtplot.
    The response delivers the binning factors, number of windows and
    their positions.
    """
    def __init__(self, instpars, port):
        # '' opens port on localhost and makes it visible
        # outside localhost
        try:
            socketserver.TCPServer.__init__(self, ('', port), RtplotHandler)
            self.instpars = instpars
        except socket.error as err:
            message = str(err) + '. '
            message += 'Failed to start the rtplot server. '
            message += 'There may be another instance of usdriver running. '
            message += 'Suggest that you shut down hdriver, close all other instances,'
            message += ' and then restart it.'
            raise DriverError(message)
        print('rtplot server started')

    def run(self, g):
        try:
            self.serve_forever()
        except Exception as e:
            g.clog.warn('RtplotServer.run', e)
