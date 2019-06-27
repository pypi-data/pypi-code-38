from queue import Queue

from api.exceptions import ServiceInnerException
from api.model import OutputWrapper
from api.model.OtherTargetOutputPipe import OtherTargetOutputPipe
from api.model.ReadWriteLock import ReadWriteLock


class BatchOutputPipe:
    __output_stream: Queue = None
    __output_count = 0
    __lock = ReadWriteLock()

    def __init__(self, output_stream, output_count):
        self.__output_stream = output_stream
        self.__output_count = output_count

    def clean(self):
        self.__lock.acquire_read()
        try:
            self.__output_stream.put_nowait(OutputWrapper.CLEAN())
        except Exception as e:
            raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
        finally:
            self.__lock.release_read()

        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def output_for_insert(self, serializable):
        self.__lock.acquire_read()
        try:
            self.__output_stream.put_nowait(OutputWrapper.INSERT(serializable))
        except Exception as e:
            raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
        finally:
            self.__lock.release_read()

        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def output_for_delete(self, query):
        self.__lock.acquire_read()
        try:
            self.__output_stream.put_nowait(OutputWrapper.DELETE(query))
        except Exception as e:
            raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
        finally:
            self.__lock.release_read()

        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def output_for_update(self, serializable):
        self.__lock.acquire_read()
        try:
            self.__output_stream.put_nowait(OutputWrapper.UPDATE(serializable))
        except Exception as e:
            raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
        finally:
            self.__lock.release_read()

        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def output_for_upsert(self, serializable):
        self.__lock.acquire_read()
        try:
            self.__output_stream.put_nowait(OutputWrapper.UPSERT(serializable))
        except Exception as e:
            raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
        finally:
            self.__lock.release_read()

        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def skip_output(self):
        return OtherTargetOutputPipe(self.__output_stream, 1, self.__output_count, self.__lock)

    def is_all_empty(self):
        self.__lock.acquire_write()
        try:
            return self.__output_stream.empty()
        finally:
            self.__lock.release_write()
