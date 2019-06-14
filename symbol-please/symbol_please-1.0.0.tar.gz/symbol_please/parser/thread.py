"""Parsing thread for symbol_please."""
import asyncio
import logging
import threading

from symbol_please.parser.client import ParserClient

_LOGGER = logging.getLogger(__name__)


class ParserThread(threading.Thread):
    """Log parsing thread."""

    def __init__(self, config):
        """Create the parser thread object."""
        super().__init__(name=self.__class__.__name__)
        self._config = config
        self._exit_event = threading.Event()
        self._client = ParserClient(config)

    def run(self):
        """Runs the log parsing thread."""
        filename = self._config['log_file']
        _LOGGER.info("Opening log file '%s'", filename)
        with open(filename, buffering=1) as logfile:
            # Read to current file position
            while logfile.readline():
                continue

            # Run the event loop
            asyncio.new_event_loop().run_until_complete(self._main(logfile))
        _LOGGER.info("Parsing thread exiting")

    async def _main(self, logfile):
        """Main coroutine function for event loop."""
        while not self._exit_event.is_set():
            # readline is technically blocking IO, but we'll allow it since
            # it'll never be more than one line, and is preferable to the
            # overhead of offloading file reading to another separate thread.
            line = logfile.readline()

            if not line:
                await asyncio.sleep(0.2)
                continue

            line = line.strip()
            if not line:
                # Skip empty lines that sneak in
                continue
            self._client.parse_raw_line(line)

    def stop(self):
        """Stop the parser thread."""
        self._exit_event.set()
        self.join()

    @property
    def client(self):
        """Get the client object."""
        return self._client
