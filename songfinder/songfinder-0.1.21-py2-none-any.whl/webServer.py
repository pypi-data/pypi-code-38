# -*- coding: utf-8 -*-

import os
from flask import Flask, request
# ~ from flask_socketio import SocketIO, emit
# ~ from flask_sse import sse
import threading
import multiprocessing
# ~ from werkzeug.serving import make_server

from songfinder.elements import elements, exports
from songfinder import classPaths



app = Flask(__name__)
# ~ app.debug = True
# ~ app.threaded=True
# ~ app.run(threaded=True)
# ~ socketio = SocketIO(app)

@app.route('/')
def hello_world(html=None):
	chemin = os.path.join(classPaths.PATHS.songs, 'SUP112 Ce nom si merveilleux.sfs')
	element = elements.Chant(chemin)
	export = exports.ExportHtml(element)
	html = export.exportText
	return html

class FlaskServer(object):
	def __ini__(self):
		pass
	# ~ def start(self):
		# ~ app.run(threaded=True)
		# ~ self._worker = threading.Thread(target=app.run)#, kwargs={'debug':True})
		# ~ self._worker = multiprocessing.Process(target=app.run)#, kwargs={'debug':True})
		# ~ self._worker.daemon = True
		# ~ self._worker.start()

	def run(self):
		app.run()
		# ~ self._worker = threading.Thread(target=socketio.run, args=(app,))
		# ~ self._worker.start()

	# ~ def _shutdown_server(self):
		# ~ func = request.environ.get('werkzeug.server.shutdown')
		# ~ if func is None:
			# ~ raise RuntimeError('Not running with the Werkzeug Server')
		# ~ func()

	# ~ @app.route('/shutdown', methods=['POST'])
	# ~ def stop(self):
		# ~ self._shutdown_server()
		# ~ return 'Server shutting down...'

# ~ @socketio.on('my event')                          # Decorator to catch an event called "my event":
# ~ def test_message(message):                        # test_message() is the event callback function.
	# ~ emit('my response', {'data': 'got it!'})      # Trigger a new event called "my response"
												  # ~ # that can be caught by another callback later in the program.
# ~ app.config["REDIS_URL"] = "redis://localhost"
# ~ app.register_blueprint(sse, url_prefix='/stream')

@app.route('/send')
def send_message():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"


# ~ class FlaskServer(threading.Thread):
	# ~ def __init__(self):
		# ~ threading.Thread.__init__(self)
		# ~ self.srv = make_server('127.0.0.1', 5000, app)
		# ~ self.ctx = app.app_context()
		# ~ self.ctx.push()

	# ~ def run(self):
		# ~ self.srv.serve_forever()

	# ~ def shutdown(self):
		# ~ self.srv.shutdown()
