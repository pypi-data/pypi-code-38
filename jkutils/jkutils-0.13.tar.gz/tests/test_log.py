import logging
import threading
import time

from jkutils.logger import JKLogger, ThreadLocalStorage

from . import logger


class A:
    pass


def test_log():
    logger.debug("debug")
    logger.info("info")
    logger.set_default_fields(log_id=logger.log_id, default_id="000000000")
    logger.warning("warning")
    logger.warn("warn")
    logger.error("error")
    logger.remove_default_field("default_id", "test_id")
    logger.critical("critical")
    logger.info("dict", uid=123, phone="12774147414")
    logger.remove_default_all_fields()
    logging.info("logging info")

    logger.info({"qwe": A()})
    logger.info(A())
    assert 1


class T(threading.Thread):
    def __init__(self, log):
        super().__init__()
        self.log = log

    def run(self):
        self.log.set_default_fields(log_id=self.log.log_id, thread_name="=====" + threading.current_thread().name)
        self.log.warning("start")
        time.sleep(2)
        self.log.warning("end")


def test_thread():
    log = JKLogger("thread", default_fileds_obj=ThreadLocalStorage())
    for _ in range(3):
        T(log).start()
    time.sleep(3)
    assert 1
