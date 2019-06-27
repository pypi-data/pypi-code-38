from queue import Queue

from api.exceptions import ServiceInnerException
from api.model import OutputWrapper
from api.model.ReadWriteLock import ReadWriteLock


class OtherTargetOutputPipe:
    __index = 1
    __output_stream: Queue = None
    __output_count = 0
    __lock = ReadWriteLock()

    def __init__(self, output_stream, index, output_count, lock):
        self.__output_stream = output_stream
        self.__lock = lock
        self.__index = index
        self.__output_count = output_count

    def then_output_for_insert(self, callable_func):
        # 必须保证callable不为空, 并且 当前的输出层级 小于输出目标的个数,才能执行输出.
        # 比如outputFdCode配置的是:["a","b"]两个. 那么outputCount = 2. 第一次进入thenOutputForInsert的时候index=1 满足要求,允许输出.
        # 如果这个时候再调用 thenOutputForInsert index=2 那么就不会再执行callable里面的东西了,因为就算执行了,也没有对应的outputfd提供输出.
        if callable_func is not None and self.__output_count > self.__index:
            self.__lock.acquire_read()
            try:
                contents = callable_func()
                if contents is not None:
                    if isinstance(contents, list):
                        for content in contents:
                            self.__output_stream.put_nowait(OutputWrapper.INSERT(content, self.__index))
                    else:
                        self.__output_stream.put_nowait(OutputWrapper.INSERT(contents, self.__index))
            except Exception as e:
                raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
            finally:
                self.__lock.release_read()

        self.__index = self.__index + 1
        return self

    def then_flat_output_for_updates(self, callable_func):
        # 必须保证callable不为空, 并且 当前的输出层级 小于输出目标的个数,才能执行输出.
        # 比如outputFdCode配置的是:["a","b"]两个. 那么outputCount = 2. 第一次进入thenOutputForInsert的时候index=1 满足要求,允许输出.
        # 如果这个时候再调用 thenOutputForInsert index=2 那么就不会再执行callable里面的东西了,因为就算执行了,也没有对应的outputfd提供输出.
        if callable_func is not None and self.__output_count > self.__index:
            self.__lock.acquire_read()
            try:
                contents = callable_func()
                if contents is not None:
                    if isinstance(contents, list):
                        for content in contents:
                            self.__output_stream.put_nowait(OutputWrapper.UPDATE(content, self.__index))
                    else:
                        self.__output_stream.put_nowait(OutputWrapper.UPDATE(contents, self.__index))
            except Exception as e:
                raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
            finally:
                self.__lock.release_read()

        self.__index = self.__index + 1
        return self

    def then_flat_output_for_upserts(self, callable_func):
        # 必须保证callable不为空, 并且 当前的输出层级 小于输出目标的个数,才能执行输出.
        # 比如outputFdCode配置的是:["a","b"]两个. 那么outputCount = 2. 第一次进入thenOutputForInsert的时候index=1 满足要求,允许输出.
        # 如果这个时候再调用 thenOutputForInsert index=2 那么就不会再执行callable里面的东西了,因为就算执行了,也没有对应的outputfd提供输出.
        if callable_func is not None and self.__output_count > self.__index:
            self.__lock.acquire_read()
            try:
                contents = callable_func()
                if contents is not None:
                    if isinstance(contents, list):
                        for content in contents:
                            self.__output_stream.put_nowait(OutputWrapper.UPSERT(content, self.__index))
                    else:
                        self.__output_stream.put_nowait(OutputWrapper.UPSERT(contents, self.__index))
            except Exception as e:
                raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
            finally:
                self.__lock.release_read()

        self.__index = self.__index + 1
        return self

    def then_flat_output_for_delete(self, callable_func):
        # 必须保证callable不为空, 并且 当前的输出层级 小于输出目标的个数,才能执行输出.
        # 比如outputFdCode配置的是:["a","b"]两个. 那么outputCount = 2. 第一次进入thenOutputForInsert的时候index=1 满足要求,允许输出.
        # 如果这个时候再调用 thenOutputForInsert index=2 那么就不会再执行callable里面的东西了,因为就算执行了,也没有对应的outputfd提供输出.
        if callable_func is not None and self.__output_count > self.__index:
            self.__lock.acquire_read()
            try:
                contents = callable_func()
                if contents is not None:
                    if isinstance(contents, list):
                        for content in contents:
                            self.__output_stream.put_nowait(OutputWrapper.DELETE(content, self.__index))
                    else:
                        self.__output_stream.put_nowait(OutputWrapper.DELETE(contents, self.__index))
            except Exception as e:
                raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
            finally:
                self.__lock.release_read()

        self.__index = self.__index + 1
        return self

    def then_clean(self):
        # 必须保证callable不为空, 并且 当前的输出层级 小于输出目标的个数,才能执行输出.
        # 比如outputFdCode配置的是:["a","b"]两个. 那么outputCount = 2. 第一次进入thenOutputForInsert的时候index=1 满足要求,允许输出.
        # 如果这个时候再调用 thenOutputForInsert index=2 那么就不会再执行callable里面的东西了,因为就算执行了,也没有对应的outputfd提供输出.
        if self.__output_count > self.__index:
            self.__lock.acquire_read()
            try:
                self.__output_stream.put_nowait(OutputWrapper.CLEAN(self.__index))
            except Exception as e:
                raise ServiceInnerException(f"放入输出队列失败:{str(e)}")
            finally:
                self.__lock.release_read()

        self.__index = self.__index + 1
        return self

    def then_skip_output(self):
        self.__index = self.__index + 1
        return self
