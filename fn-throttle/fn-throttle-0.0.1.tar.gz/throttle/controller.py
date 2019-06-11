"""
Speed controller

Only master node will manage a controller object
"""
import logging
import random
import time


class AbstractController:

    def registry(self, key: str, params: dict) -> bool:
        raise NotImplementedError()

    def admit(self, key: str) -> bool:
        raise NotImplementedError()


class MinIntervalController(AbstractController):
    """ Function calls are controlled by specified minimum intervals (in seconds) """

    def __init__(self):
        self.configs = {}  # key - min_interval
        self.calls = {}  # key - last_admit_timestamp

    def registry(self, key: str, params: dict) -> bool:
        """
        :param key:
        :param params: {'min_interval': float}
        """
        try:
            if 'min_interval' in params:
                self.configs[key] = float(params['min_interval'])
                return True
            else:
                return False
        except Exception as e:
            logging.error(f'In {self.__class__}.registry, params: {params}, error: {e}', exc_info=True)
            return False

    def admit(self, key: str) -> bool:
        if key not in self.calls:
            self.calls[key] = time.time()
            return True
        else:
            last_admit_timestamp = self.calls[key]
            current_timestamp = time.time()
            if current_timestamp - last_admit_timestamp >= self.configs[key]:
                self.calls[key] = current_timestamp
                return True
            else:
                return False


class MockController(AbstractController):

    def registry(self, key: str, params: dict) -> bool:
        ret = random.random() < 0.5
        logging.info(f'In {self.__class__}.registry, key: {key}, params: {params}, ret: {ret}')
        return ret

    def admit(self, key: str) -> bool:
        ret = random.random() < 0.5
        logging.info(f'In {self.__class__}.admit, key: {key}, ret: {ret}')
        return ret
