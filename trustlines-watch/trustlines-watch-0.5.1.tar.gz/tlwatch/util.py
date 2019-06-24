import sys
import time
import logging
import pkg_resources

logger = logging.getLogger(__name__)


def get_version():
    return pkg_resources.get_distribution("trustlines-watch").version


def decode_hex_encoded_number(s: str):
    if not s.startswith("0x"):
        raise RuntimeError("could not decode number {!r}".format(s))
    return int(s[2:], 16)


def watch_report_loop(get_riemann_client, watch, sleep_time):
    """watch some service for events and send them to riemann forever

    This function periodically calls the given function watch. watch should
    return a list of dictionaries suitable for sending to riemann. It then sends
    those events to riemann and sleep for sleep_time seconds.
    """
    while 1:
        try:
            lst = watch()
            client = get_riemann_client()
            for x in lst:
                client.send(x)
        except KeyboardInterrupt:
            raise
        except BaseException:
            logger.critical("Error in watch", exc_info=sys.exc_info())
        time.sleep(sleep_time)
