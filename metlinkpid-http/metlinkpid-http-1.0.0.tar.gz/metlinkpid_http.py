"""
Usage:
  metlinkpid-http [--serial=PORT] [--http=HOST:PORT]
  metlinkpid-http (-h | --help)

Options:
  --serial=PORT
      The PID serial port [default: /dev/ttyUSB0].
      Can be set using environment variable METLINKPID_SERIAL.

  --http=HOST:PORT
      The hostname/IP address and port to listen on [default: 127.0.0.1:8080].
      Use an IP address of "0.0.0.0" to listen on all IP addresses.
      Can be set using environment variable METLINKPID_HTTP.

Full documentation online at:
  https://github.com/Lx/python-metlinkpid-http
"""

from sys import stderr
from threading import Lock, Event, Thread
from urllib.parse import unquote_plus

from envopt import envopt
from flask import Flask, request, jsonify
from metlinkpid import PID
from waitress import serve

PING_INTERNAL_SEC = 10


def main():
    args = envopt(__doc__, prefix='METLINKPID_')

    try:
        pid = PID.for_device(args['--serial'])
    except Exception as e:
        exit('metlinkpid-http: {}'.format(e))

    pid_lock = Lock()

    app = Flask(__name__)

    @app.route("/")
    def send_message():
        message = unquote_plus(request.query_string.decode('utf-8'))
        json = {'message': message, 'error': None}
        try:
            with pid_lock:
                pid.send(message)
        except Exception as e:
            json['error'] = str(e)
        return jsonify(json)

    ping_event = Event()

    def ping():
        while True:
            with pid_lock:
                try:
                    pid.ping()
                except Exception as e:
                    print('metlinkpid-http: {}'.format(e), file=stderr)
            if ping_event.wait(PING_INTERNAL_SEC):
                break

    Thread(target=ping).start()
    try:
        serve(app, listen=args['--http'], threads=1)
    finally:
        ping_event.set()


if __name__ == '__main__':
    main()
