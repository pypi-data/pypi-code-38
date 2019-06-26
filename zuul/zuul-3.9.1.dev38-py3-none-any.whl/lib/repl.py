# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Based on ASL2 code from:
# https://gist.github.com/tim-patterson/4471877

import sys
import io
import threading
import socketserver
import code


class ThreadLocalProxy(object):
    def __init__(self, default):
        self.files = {}
        self.default = default

    def __getattr__(self, name):
        obj = self.files.get(threading.currentThread(), self.default)
        return getattr(obj, name)

    def register(self, obj):
        self.files[threading.currentThread()] = obj

    def unregister(self):
        self.files.pop(threading.currentThread())


class REPLHandler(socketserver.StreamRequestHandler):
    def handle(self):
        sys.stdout.register(io.TextIOWrapper(self.wfile, 'utf8'))
        sys.stderr.register(io.TextIOWrapper(self.wfile, 'utf8'))
        sys.stdin.register(io.TextIOWrapper(self.rfile, 'utf8'))
        try:
            console = code.InteractiveConsole(locals())
            console.interact('Console:')
        except Exception:
            pass
        finally:
            sys.stdout.unregister()
            sys.stderr.unregister()
            sys.stdin.unregister()


class REPLThreadedTCPServer(socketserver.ThreadingMixIn,
                            socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, scheduler, *args, **kw):
        self.scheduler = scheduler
        super(REPLThreadedTCPServer, self).__init__(*args, **kw)
        sys.stdout = ThreadLocalProxy(sys.stdout)
        sys.stderr = ThreadLocalProxy(sys.stderr)
        sys.stdin = ThreadLocalProxy(sys.stdin)


class REPLServer(object):
    def __init__(self, scheduler):
        self.server = REPLThreadedTCPServer(
            scheduler, ('localhost', 3000), REPLHandler)

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(10)
