# encoding:utf-8

from __future__ import unicode_literals
import base64
import datetime
import gzip
import json
import os
import re
import threading
import time

import requests
from requests import ConnectionError

from tgasdk.TGAException import TGAException, TGAIllegalDataException

SDK_VERSION = '1.1.23'
try:
    import queue
except ImportError:
    import Queue as queue

try:
    isinstance("", basestring)
    def is_str(s):
        return isinstance(s, basestring)
except NameError:
    def is_str(s):
        return isinstance(s, str)

try:
    isinstance(1, long)
    def is_int(n):
        return isinstance(n, int) or isinstance(n, long)
except NameError:
    def is_int(n):
        return isinstance(n, int)

class TGAnalytics(object):
    """
    TGAnalytics construct

    :param consumer: 数据格式化和传输方式.
    """

    def __init__(self, consumer):
        self.__consumer = consumer
        self.__super_properties = {}
        self.clear_super_properties()
        self.track_pattern = re.compile(r"^(#[a-z][a-z0-9_]{0,49})|([a-z][a-z0-9_]{0,50})$", re.I)
        self.user_pattern = re.compile(r"^(#[a-z][a-z0-9_]{0,49})|([a-z][a-z0-9_]{0,50})$", re.I)

    """
    :param distinct_id: 匿名id
    :param account_id:  注册id
    :param properties:  属性
    """

    def user_set(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_set', None, properties)

    def user_setOnce(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_setOnce', None, properties)

    def user_add(self, distinct_id=None, account_id=None, properties=None):
        self.__add(distinct_id, account_id, 'user_add', None, properties)

    def user_del(self, distinct_id=None, account_id=None, properties=None):
        if properties == None:
            properties['#time'] = datetime.datetime.now()
        self.__add(distinct_id, account_id, 'user_del', None, properties)

    def track(self, distinct_id=None, account_id=None, event_name=None, properties=None):
        all_properties = self.__super_properties.copy()
        if properties:
            all_properties.update(properties)
        if not is_str(event_name):
            raise TGAIllegalDataException('Event_name of track is invalid,it must be set a str')

        self.__add(distinct_id, account_id, 'track', event_name, all_properties)

    def flush(self):
        self.__consumer.flush()

    def close(self):
        self.__consumer.close()

    def __add(self, distinct_id, account_id, type, event_name, properties_add):
        if properties_add:
            properties = properties_add.copy()
        else:
            properties = {}
        if distinct_id == None and account_id == None:
            raise TGAException("Distinct_id and account_id must be set at least one")

        self.__assertProperties(type, properties)
        time_event = properties.get("#time",)
        del (properties['#time'])

        ip = properties.get("#ip", "")
        if "#ip" in properties.keys():
            del (properties['#ip'])
        if 'track' == type:
            data = {
                '#time': time_event,
                '#ip': ip,
                '#type': type,
                '#event_name': event_name,
                'properties': properties
            }
        else:
            data = {
                '#time': time_event,
                '#ip': ip,
                '#type': type,
                'properties': properties
            }
        if distinct_id != None:
            data['#distinct_id'] = distinct_id
        if account_id != None:
            data['#account_id'] = account_id

        # self.__consumer.add(str(data))#python3
        self.__consumer.add(json.dumps(data))  # python2

    def __assertProperties(self, action_type, properties):
        key_pattern = self.__getKeyNamePattern(action_type)
        if properties is not None:

            if "#time" not in properties.keys():
                properties['#time'] = datetime.datetime.now()
            else:
                try:
                    time_temp = properties.get('#time')
                    if isinstance(time_temp, datetime.datetime) or isinstance(time_temp, datetime.date):
                        pass
                    else:
                        raise TGAIllegalDataException('#time only with datetime.datetime or datetime.date')
                except Exception as e:
                    raise TGAIllegalDataException(e)
            for key, value in properties.items():
                if not is_str(key):
                    raise TGAIllegalDataException("property key must be a str. [key=%s]" % str(key))
                if value is None:
                    continue
                # if len(key) > 50:
                #     raise TGAIllegalDataException("the max length of property key is 50. [key=%s]" % str(key))
                if not key_pattern.match(key):
                    raise TGAIllegalDataException(
                        "type[%s] property key must be a valid variable name. [key=%s]" % (action_type, str(key)))

                if not is_str(value) and not is_int(value) and not isinstance(value, (float)) and not isinstance(value, (bool)) and not isinstance(value,
                                                                                                                 datetime.datetime) and not isinstance(
                        value, datetime.date):
                    raise TGAIllegalDataException(
                        "property value must be a str/int/float/bool/datetime/date. [value=%s]" % type(value))
                if 'user_add' == action_type.lower() and not self.__number(value) and not key.startswith('#'):
                    raise TGAIllegalDataException('user_add must be number')
                if isinstance(value, datetime.datetime):
                    properties[key] = value.strftime('%Y-%m-%d %H:%M:%S') + ".000"
                elif isinstance(value, datetime.date):
                    properties[key] = value.strftime('%Y-%m-%d')

    def __number(self, s):
        if is_int(s):
            return True
        if isinstance(s, float):
            return True
        return False

    def __getKeyNamePattern(self, type):
        if 'track' == type:
            return self.track_pattern
        else:
            return self.user_pattern

    def clear_super_properties(self):
        """
        删除所有已设置的事件公共属性
        """
        self.__super_properties = {
            '#lib': 'tga_python_sdk',
            '#lib_version': SDK_VERSION,
        }

    def set_super_properties(self, properties):
        """
        设置每个事件都带有的一些公共属性，当 track 的 properties 和 super properties 有相同的 key 时，将采用 track 的

        :param super_properties 公共属性
        """
        self.__super_properties.update(properties)


if os.name == 'nt':
    import msvcrt

    def lock(file_):
        try:
            savepos = file_.tell()
            file_.seek(0)
            try:
                msvcrt.locking(file_.fileno(), msvcrt.LK_LOCK, 1)
            except IOError as e:
                raise TGAException(e)
            finally:
                if savepos:
                    file_.seek(savepos)
        except IOError as e:
            raise TGAException(e)

    def unlock(file_):
        try:
            savepos = file_.tell()
            if savepos:
                file_.seek(0)
            try:
                msvcrt.locking(file_.fileno(), msvcrt.LK_UNLCK, 1)
            except IOError as e:
                raise TGAException(e)
            finally:
                if savepos:
                    file_.seek(savepos)
        except IOError as e:
            raise TGAException(e)

elif os.name == 'posix':
    import fcntl

    def lock(file_):
        try:
            fcntl.flock(file_.fileno(), fcntl.LOCK_EX)
        except IOError as e:
            raise TGAException(e)

    def unlock(file_):
        fcntl.flock(file_.fileno(), fcntl.LOCK_UN)

else:
    raise TGAException("Python SDK is defined for NT and POSIX system.")


class SAFileLock(object):
    def __init__(self, file_handler):
        self._file_handler = file_handler

    def __enter__(self):
        lock(self._file_handler)
        return self

    def __exit__(self, t, v, tb):
        unlock(self._file_handler)

class LoggingConsumer(object):
    """
    将数据使用 logging 库输出到指定路径，并默认按天切割
    """

    """
    @:param log_directory : 日志保存目录
    @:param log_size : 单个日志文件的大小，默认是1G
    @:param bufferSize : 每次写入文件的大小
    """
    _mutex = queue.Queue()

    class FileWriter(object):

        _writer_count = {}

        @classmethod
        def getCount(cls, filename):
            return cls._writer_count.get(filename,0)

        @classmethod
        def addCount(cls, filename):
            count = cls.getCount(filename)
            count = count + 1
            cls._writer_count[filename] = count

        @classmethod
        def minusCount(cls, filename):
            count = cls.getCount(filename)
            count = count - 1
            if count <= 0:
                if filename in cls._writer_count:
                    del cls._writer_count[filename]
            else:
                cls._writer_count[filename] = count

        def __init__(self, filename):
            self._filename = filename
            self._file = open(filename, 'a')
            LoggingConsumer.FileWriter.addCount(filename)

        def close(self):
            LoggingConsumer.FileWriter.minusCount(self._filename)
            if LoggingConsumer.FileWriter.getCount(self._filename) == 0:
                self._file.close()

        def isValid(self, filename):
            return self._filename == filename

        def write(self, messages):
            with SAFileLock(self._file):
                for message in messages:
                    self._file.write(message)
                    self._file.write('\n')
                self._file.flush()

    @classmethod
    def construct_filename(cls, directory, date_suffix, filesize):
        file_suffix = cls.getSplitLogSuffix(directory, date_suffix, filesize)
        return directory + "log." + date_suffix + "_" + str(file_suffix)

    @classmethod
    def getSplitLogSuffix(cls, directory, date_suffix, filesize):
        split_log_suffix = len([x for x in os.listdir(directory) if "log." + date_suffix in x])
        if split_log_suffix  != 0:
            split_log_suffix = split_log_suffix  - 1
        filename = directory + "log." + date_suffix + "_" + str(split_log_suffix)
        if(os.path.exists(filename)):
            split_log_suffix = cls.fileSizeOut(filename, filesize, split_log_suffix)
        return split_log_suffix

    @classmethod
    def fileSizeOut(cls, filePath, filesize, split_log_suffix):
        fsize = os.path.getsize(filePath)
        fsize = fsize / float(1024 * 1024)
        if fsize >= filesize:
            split_log_suffix += 1
        return split_log_suffix

    @classmethod
    def unlockLoggingConsumer(cls):
        cls._mutex.put(1)

    @classmethod
    def initlockLoggingConsumer(cls):
        cls._mutex.put(1)

    @classmethod
    def lockLoggingConsumer(cls):
        cls._mutex.get(block=True, timeout=None)

    def __init__(self, log_directory, log_size=1024, bufferSize=8192):
        self.log_directory = log_directory # log文件保存的目录
        self.sdf = '%Y-%m-%d'
        self.suffix = datetime.datetime.now().strftime(self.sdf)
        self._fileSize = log_size  # 单个log文件的大小
        if not self.log_directory.endswith("/"):
            self.log_directory = self.log_directory + "/"
        self._buffer = []
        self._bufferSize = bufferSize
        self.initlockLoggingConsumer()
        self.lockLoggingConsumer()
        filename = LoggingConsumer.construct_filename(self.log_directory, self.suffix, self._fileSize)
        self._writer = LoggingConsumer.FileWriter(filename)
        self.unlockLoggingConsumer()

    def add(self, msg):
        messages = None
        self.lockLoggingConsumer()
        self._buffer.append(msg)
        if len(self._buffer) > self._bufferSize:
            messages = self._buffer
            date_suffix = datetime.datetime.now().strftime(self.sdf)
            if self.suffix != date_suffix:
                self.suffix = date_suffix
                self._split_log_suffix = 0
            filename = LoggingConsumer.construct_filename(self.log_directory, self.suffix, self._fileSize)
            if not self._writer.isValid(filename):
                self._writer.close()
                self._writer = LoggingConsumer.FileWriter(filename)
            self._buffer = []
        self.unlockLoggingConsumer()
        if messages:
            self._writer.write(messages)

    def flushWithClose(self, is_close):
        messages = None
        self.lockLoggingConsumer()
        if len(self._buffer) > 0:
            messages = self._buffer
            filename = LoggingConsumer.construct_filename(self.log_directory, self.suffix, self._fileSize)
            if not self._writer.isValid(filename):
                self._writer.close()
                self._writer = LoggingConsumer.FileWriter(filename)
            self._buffer = []
        self.unlockLoggingConsumer()
        if messages:
            self._writer.write(messages)
        if is_close:
            self._writer.close()

    def flush(self):
        self.flushWithClose(False)

    def close(self):
        self.flushWithClose(True)

class BatchConsumer(object):
    """
    默认的 Consumer实现，逐条、同步的发送数据给接收服务器。
    """

    def __init__(self, server_uri, appid, batch=20, timeout=30000, interval=3):
        """
        Consumer construct

        :param server_uri: 服务器的 URL 地址.
        :param appid: appid一个token，来自tga官网.
        :param timeout: 请求的超时时间，单位毫秒.
        :param interval: 推送数据的最大时间间隔.
        """
        self.__server_uri = server_uri
        self.__appid = appid
        self.__timeout = timeout
        self.__interval = interval

        self.__batch = min(batch, 200)
        self.__message_channel = []
        self.__last_flush = time.time()
        self.__httpconsumer = HttpConsumer(self.__server_uri, self.__appid, self.__timeout)

    def add(self, msg):
        self.__message_channel.append(msg)
        if len(self.__message_channel) >= self.__batch or (
                    time.time() - self.__last_flush >= self.__interval and len(self.__message_channel) > 0):
            self.flush()

    def flush(self, throw_exception=True):
        try:
            if len(self.__message_channel) >= self.__batch:
                msg = self.__message_channel[:self.__batch]
            else:
                msg = self.__message_channel[:len(self.__message_channel)]
            self.__httpconsumer.send('[' + ','.join(msg) + ']')
            self.__last_flush = time.time()
            self.__message_channel = self.__message_channel[len(msg):]
        except TGAException as e:
            if throw_exception:
                raise e

    def close(self):
        while len(self.__message_channel) > 0:
            self.flush()


class AsyncBatchConsumer(object):
    """
    异步、批量发送数据的 Consumer。使用独立的线程进行数据发送，当满足以下两个条件之一时进行数据发送:
    1. 数据条数大于预定义的最大值
    2. 数据发送间隔超过预定义的最大时间
    """

    def __init__(self, server_uir, appid, interval=3, flush_size=20, queue_size=100000):
        """
        初始化 AsyncBatchConsumer。

        :param server_uri: 服务器的 URL 地址。
        :param appid: 数据传输的token。
        :param interval: 两次发送的最大间隔时间，单位秒。
        :param flush_size: 队列缓存的阈值，超过此值将立即进行发送。
        :param queue_size: 缓存队列的大小。
        """
        self.__consumer = HttpConsumer(server_uir, appid, 30000)
        self._flush_size = flush_size
        self.flush_max_time = interval

        self._queue = queue.Queue(queue_size)

        # 用于通知刷新线程应当立即进行刷新
        self.need_flush = threading.Event()
        self._flush_buffer = []

        # 初始化发送线程，并设置为 Daemon 模式
        self._flushing_thread = AsyncFlushThread(self)
        self._flushing_thread.daemon = True
        self._flushing_thread.start()

    def add(self, msg):
        # 这里不进行实际的发送，而是向队列里插入。如果队列已满，则抛出异常。
        try:
            self._queue.put_nowait(msg)
        except queue.Full as e:
            pass

    def flush(self):
        self.need_flush.set()

    def close(self):
        # 关闭时首先停止发送线程
        self._flushing_thread.stop()
        # 循环发送，直到队列和发送缓存都为空
        while not self._queue.empty() or not len(self._flush_buffer) == 0:
            if not self.persist():
                break

    def persist(self, throw_exception=False):
        """
        执行一次同步发送。 throw_exception 表示在发送失败时是否向外抛出异常。
        """
        flush_success = False
        if len(self._flush_buffer) == 0:
            for i in range(self._flush_size):
                if not self._queue.empty():
                    self._flush_buffer.append(str(self._queue.get_nowait()))
                else:
                    break
        if len(self._flush_buffer) > 0:
            for i in range(3):
                try:
                    self.__consumer.send('[' + ','.join(self._flush_buffer) + ']')
                    self._flush_buffer = []
                    flush_success = True
                    return flush_success
                except TGAException as e:
                    if throw_exception:
                        raise e
        else:
            flush_success = True
        return flush_success

class HttpConsumer(object):
    def __init__(self, server_uri, appid, timeout=30000):
        self.url = server_uri
        self.appid = appid
        self.timeout = timeout

    def send(self, data):
        """
        使用 Requests 发送数据给服务器，如果发生错误会抛出异常。
        """
        headers = {}
        headers['appid'] = self.appid
        headers['user-agent'] = 'tga-python-sdk'
        headers['version'] = SDK_VERSION
        try:
            requests.post(self.url, data=self._gzip_string(data.encode("utf-8")), headers=headers,
                          timeout=self.timeout)
            return True
        except ConnectionError as e:
            time.sleep(0.5)
            raise TGAException("Data transmission failed" + repr(e))

    def _gzip_string(self, data):
        try:
            return base64.b64encode(gzip.compress(data))
        except AttributeError:
            import StringIO

            buf = StringIO.StringIO()
            fd = gzip.GzipFile(fileobj=buf, mode="w")
            fd.write(data)
            fd.close()
            return base64.b64encode(buf.getvalue())


class AsyncFlushThread(threading.Thread):
    """
    发送数据的独立线程，在这里执行实际的网络请求。
    """

    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self._consumer = consumer
        # 用于实现安全退出
        self._stop_event = threading.Event()
        self._finished_event = threading.Event()

    def stop(self):
        """
        需要退出时调用此方法，以保证线程安全结束。
        """
        self._stop_event.set()
        self._finished_event.wait()

    def run(self):
        while True:
            # 如果 need_flush 标志位为 True，或者等待超过 flush_max_time，则继续执行
            self._consumer.need_flush.wait(self._consumer.flush_max_time)
            # 进行发送，如果成功则清除标志位
            if self._consumer.persist():
                self._consumer.need_flush.clear()
            # 发现 stop 标志位时安全退出
            if self._stop_event.isSet():
                break
        self._finished_event.set()
