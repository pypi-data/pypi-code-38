import websocket
import logging
import os
import json
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import textwrap
from csirtgsdk.constants import LOG_FORMAT
from websocket import create_connection

try:
    import thread
except ImportError:
    import _thread as thread

REMOTE = os.getenv('CIF_REMOTE_WS', 'ws://localhost:5000/firehose')

logger = logging.getLogger(__name__)

TRACE = os.environ.get('CIFSDK_CLIENT_WS_TRACE', '0')

if TRACE == '1':
    logger.setLevel(logging.DEBUG)
    logging.getLogger('websocket').setLevel(logging.DEBUG)
    websocket.enableTrace(True)

TOKEN = os.getenv('CIF_TOKEN')


class DefaultHandler(websocket.WebSocket):
    def __init__(self, remote=REMOTE, token=TOKEN, **kvargs):

        self.handle = websocket.WebSocketApp(
            remote,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            header={'Authorization: ' + token},
        )

        self.error = False

    def on_message(self, ws, message):
        logger.debug(message)

        if isinstance(message, bytes):
            message = message.decode('utf8')

        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            pass

        if message == 'ping':
            self.handle.send('pong')
            return

        if message == 'connected' and logger.getEffectiveLevel() == logging.DEBUG:
            print('connected...')
            return

        if logger.getEffectiveLevel() == logging.DEBUG:
            print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))
        else:
            print(json.dumps(message))

    def on_error(self, ws, error):
        if len(str(error)):
            logger.error(error)
            self.error = True

    def connected(self, ws, **kwargs):
        logger.info('connected...')

    def on_close(self, ws):
        logger.info(' ### CLOSED ###')

    def on_open(self, ws):
        pass

    def run(self):
        self.handle.run_forever()


def main():
    class MyHandler(DefaultHandler):
        def on_close(self, ws):
            ws.close()
            logger.info("Closed using MyHandler...")

    parser = ArgumentParser(
        description=textwrap.dedent('''\
            example usage:
              $ export CIF_TOKEN=abcdefg1234...
              $ cif-firehose -v
            '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif-firehose'
    )

    parser.add_argument("-v", "--verbose", action="count", help="set verbosity level to INFO")
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-r', '--reconnect', action="store_true", help="auto reconnect if connection closes...", default=False)

    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.verbose:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG

    logger.setLevel(loglevel)

    console = logging.StreamHandler()
    logging.getLogger('').setLevel(loglevel)
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(console)

    h = MyHandler()

    while True:
        h.run()

        # if we closed and it wasn't an error
        if not h.error:
            break

        # if we didn't set the re-connect flag
        if not args.reconnect:
            break

        # we set the re-connect and it was an error, clear the error and re-connect.
        h.error = False

        logger.info('re-connecting..')


if __name__ == "__main__":
    main()
