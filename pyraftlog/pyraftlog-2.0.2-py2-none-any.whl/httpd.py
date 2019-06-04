# @TODO Convert to `http.server` in py3
import BaseHTTPServer
# @TODO Convert to `socketserver` in py3
import SocketServer
import json
import re
import time

from pyraftlog.node import get_mode_name


class RaftHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    raft = None
    transport = None
    consensus_timeout = 3.0

    def serve_forever(self, poll_interval=0.5):
        while not self.raft.shutdown_flag:
            self.handle_request()


class RaftHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = 'RaftHTTP/1.0'
    sys_version = ''
    error_message_format = '{"code":%(code)d}'
    error_content_type = 'application/json'
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        pass

    def redirect_location(self):
        """
        :return: The location where commands should be sent
        :rtype: str
        """
        address = self.server.raft.get_request_address()
        if address:
            return self.server.raft.get_request_address() + self.path

    def _send_leader_redirect(self):
        """ Send a redirect response that will point the requester at the leader. """
        if self.redirect_location():
            self.send_response(307)
            self.send_header('Connection', 'Close')
            self.send_header('Location', self.redirect_location())
            self.end_headers()
        else:
            self._send_headers_and_response(503, json.dumps({'message': 'This Node has no defined leader'}))

    def _send_headers_and_response(self, code, response=None):
        """ Send the headers and body back to the requester. """
        self.send_response(code)
        self.send_header('Connection', 'Keep-Alive')
        self.send_header('Keep-Alive', 'timeout=5, max=100')
        if response is not None:
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
        if self.server.raft.get_leader():
            self.send_header('Leader-Location', self.server.raft.get_request_address())
        self.end_headers()

        self.wfile.write(response)

    def is_valid(self, data):
        """
        :param data: Data to be checked
        :type data: str
        :return: True if given data is valid
        :rtype: bool
        """
        return True

    def do_HEAD(self):
        # If not leader redirect request
        if not self.server.raft.is_leader():
            self._send_leader_redirect()

        elif self.path == '/' or self.path == '':
            self.send_response(204)
            self.end_headers()

        else:
            self.send_error(404, 'Not found')

    def do_GET(self):
        raft = self.server.raft

        if self.path == '/' or self.path == '':
            neighbours = []
            for neighbour in raft.neighbours:
                data = {
                    "name": neighbour,
                    "connected": self.server.transport.is_connected(neighbour),
                    "last_heard": raft.last_heard[neighbour],
                }
                if raft.is_leader():
                    data.update({
                        "next_index": raft.state.next_index[neighbour],
                        "match_index": raft.state.match_index[neighbour],
                        "synchronised": raft.synchronised[neighbour],
                    })
                neighbours.append(data)
            response = json.dumps({
                "up_time": time.time() - raft.start_time,
                "time_in_state": time.time() - raft.state.time_in_state,
                "term": raft.state.current_term,
                "committed": {
                    "term": raft.state.log.get(raft.state.commit_index).term,
                    "index": raft.state.log.get(raft.state.commit_index).idx,
                },
                "cluster_applied": raft.state.cluster_applied,
                "logs": len(raft.state.log),
                "is_leader": raft.is_leader(),
                "leader": raft.get_leader(),
                "neighbours": neighbours,
                "request_address": raft.get_request_address(),
                "status": raft.status(),
                "state": str(raft.state),
            })

            self._send_headers_and_response(200, response)
        elif self.path.startswith('/log'):
            if self.path == '/log':
                response = json.dumps(raft.state.log.values(0, raft.state.last_applied))
                self._send_headers_and_response(200, response)
            else:
                search = re.search(r'^/log/([0-9])$', self.path)
                if not search:
                    self._send_headers_and_response(404, json.dumps({'message': 'Log unavailable'}))
                    return

                if search.group(1):
                    log_index = int(search.group(1))
                    response = raft.state.get_current_state(log_index)
                    if not response:
                        self._send_headers_and_response(404, json.dumps({'message': 'Log unavailable'}))
                    else:
                        self._send_headers_and_response(200, json.dumps(response))
                else:
                    self._send_headers_and_response(404, json.dumps({'message': 'Not Found'}))
        elif self.path == '/stats':
            if raft.is_leader():
                response = raft.state.statistics.generate_statistics()
                if response:
                    self._send_headers_and_response(200, json.dumps(response))
                else:
                    self._send_headers_and_response(409, json.dumps({'message': 'No samples available'}))
            else:
                self._send_leader_redirect()

    def do_POST(self):
        raft = self.server.raft
        # If there isn't a leader
        if not raft.get_leader():
            self._send_headers_and_response(503, json.dumps({'message': 'This Node has no defined leader'}))
        elif self.path == '/':
            if not raft.is_leader():
                self._send_leader_redirect()
            # If not enough connected nodes to make a majority
            elif not raft.has_majority(len(self.server.transport.connected()) + 1):
                self._send_headers_and_response(503, json.dumps({'message': 'Service Unavailable'}))
            # Validate request
            elif self.headers['Content-Type'] == 'application/json':
                # Read and parse request data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                parsed_data = json.loads(post_data)

                # Validate the incoming command
                if not self.is_valid(parsed_data):
                    self._send_headers_and_response(400, json.dumps({'message': 'Bad Request'}))
                    return

                # Attempt to write to log and wait for consensus
                raft.logger.debug('[%-9s] Command received: %s', raft.state, post_data)
                index = raft.append_entry(parsed_data)
                timeout = time.time() + self.server.consensus_timeout
                while timeout > time.time() and raft.state.last_applied < index and raft.state.commit_index < index:
                    pass

                response = json.dumps({'index': index})
                if raft.state.last_applied >= index:
                    self._send_headers_and_response(201, response)
                elif raft.state.commit_index >= index:
                    self._send_headers_and_response(202, response)
                else:
                    self._send_headers_and_response(500, json.dumps({'message': 'Internal Server Error'}))
                raft.state.statistics.set_responded_timestamp(index, time.time())
        elif self.path == '/log':
            # Validate request
            parsed_data = None
            if self.headers['Content-Type'] == 'application/json':
                # Read and parse request data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                parsed_data = json.loads(post_data)

            if parsed_data:
                # Deactivate the node but keep http running
                raft.deactivate()

                # Load the new storage data
                raft.reset_state(parsed_data)

                # Activate the node
                raft.activate(raft.transport)

                self._send_headers_and_response(204)
            else:
                self._send_headers_and_response(404, json.dumps({'message': 'Invalid request received'}))
        else:
            self.send_error(404, 'Not found')

    def do_PATCH(self):
        raft = self.server.raft

        if self.path == '/' or self.path == '':
            # Check content type
            if not self.headers['Content-Type'] or self.headers['Content-Type'] != 'application/json':
                self.send_error(404, 'Content-Type must be application/json')

            # Check content length
            if not self.headers['Content-Length']:
                self.send_error(404, 'Content-Length is required')

            # Read and parse request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = json.loads(post_data)

            # Update activeness
            if 'active' in parsed_data:
                if parsed_data['active'] and not raft.active:
                    raft.activate(raft.transport)
                elif not parsed_data['active'] and raft.active:
                    raft.deactivate()
                else:
                    self._send_headers_and_response(409, json.dumps({'message': 'Conflict'}))
                    return

            # Update mode
            if 'mode' in parsed_data:
                raft.mode = get_mode_name(parsed_data['mode'])

            self._send_headers_and_response(204)
        else:
            self.send_error(404, '')
