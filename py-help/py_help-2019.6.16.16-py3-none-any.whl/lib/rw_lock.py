import threading


class RwLock(object):
    def __init__(self):
        self.__monitor = threading.Lock()
        self.__exclude = threading.Lock()
        self.readers = 0

    def acquire_read(self):
        with self.__monitor:
            self.readers += 1
            if self.readers == 1:
                self.__exclude.acquire()

    def release_read(self):
        with self.__monitor:
            self.readers -= 1
            if self.readers == 0:
                self.__exclude.release()

    def acquire_write(self):
        self.__exclude.acquire()

    def release_write(self):
        self.__exclude.release()
