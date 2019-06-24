""" dota2gsi.py """
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads as json_loads

class MyServer(HTTPServer):
    def init_state(self):
        self.last_state = None
        self.handlers = []
        self.on_ability_cast = []

    def handle_state(self, state):
        for handler in self.handlers:
            handler(self.last_state, state)

        if len(self.on_ability_cast) > 0:
            if state and self.last_state:
                # Iterate through all 10 ability slots
                for i in range(10):
                    ability = state.get('abilities', {}).get(f'ability{i}')
                    last_ability = self.last_state.get('abilities', {}).get(f'ability{i}')
                    if ability and last_ability:
                        # If the spell was previously castable
                        if last_ability.get('can_cast'):
                        # and the cooldown has increased, then the spell was just cast
                            if int(ability.get('cooldown')) > int(last_ability.get('cooldown')):
                                for f in self.on_ability_cast:
                                    f(state, ability)

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """ Receive state from GSI """
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')
        state = json_loads(body)
        self.send_header('Content-type', 'text/html')
        self.send_response(200)
        self.end_headers()
        self.server.handle_state(state)
        self.server.last_state = state

    def log_message(self, format, *args):
        """ Don't print status messages """
        return

class Server():
    def __init__(self, ip='0.0.0.0', port=3000):
        self.ip = ip
        self.port = port
        self.server = MyServer((ip, port), MyRequestHandler)
        self.server.init_state()

    def start(self):
        print(f"DotA 2 GSI server listening on {self.ip}:{self.port} - CTRL+C to stop")
        if len(self.server.handlers) == 0 and len(self.server.on_ability_cast) == 0:
            print("Warning: no handlers were added, nothing will happen")
        try:
            self.server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        self.server.server_close()
        print("Server stopped.")

    def on_update(self, func):
        """ Sets the function to be called when a new state is available
        
        The function must accept two arguments:
            last_state - the previous state
            state - the new state
        """
        self.server.handlers.append(func)
        

    def on_ability_cast(self, func):
        """ Sets the function to be called when an ability is cast
        
        The function must accept two arguments:
            state - the current state
            ability - the ability that was cast
        """
        self.server.on_ability_cast.append(func)