import platform
import socket

from .logger import logger


def add_info(obj):
    try:
        obj.hostname = socket.gethostname()
    except Exception:
        logger.warning("Failed to get hostname", exc_info=1)
        obj.hostname = ""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        obj.ip = s.getsockname()[0]
    except Exception:
        logger.warning("Failed to get ip", exc_info=1)
        obj.ip = ""
    finally:
        s.close()

    obj.machine_type = platform.machine()
    obj.network = platform.node()

    obj.os = platform.system()
    obj.os_release = platform.release()
    obj.os_version = platform.version()
    obj.os_string = platform.platform()
