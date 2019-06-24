import logging
from bluemax.scripts.pid_script import Stoppable


logger = logging.getLogger(__name__)


class Worker(Stoppable):
    def start(self):
        """
            Called as console_script to run the
            worker using redis.
        """
        from bluemax.web.settings import load_config, options
        from bluemax.work import worker

        load_config(".env")
        logger.info("hello from worker! mode:%s", "debug" if options.debug else "prod")
        worker.main()


def main():
    Worker().main()


if __name__ == "__main__":
    main()
