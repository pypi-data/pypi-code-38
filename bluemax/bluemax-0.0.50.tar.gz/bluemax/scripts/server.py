import logging
from bluemax.scripts.pid_script import Stoppable


logger = logging.getLogger(__name__)


class Server(Stoppable):
    def start(self):
        """
            Called as console_script to run the
            server - either standalone or as manager
            of workers using redis.
        """
        from bluemax.web.settings import load_config, options
        from bluemax.web import server

        load_config(".env")
        logger.info("mode:%s", "debug" if options.debug else "prod")
        server.main()


def main():
    Server().main()


if __name__ == "__main__":
    main()
