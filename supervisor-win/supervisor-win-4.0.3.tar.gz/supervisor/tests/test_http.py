import base64
import os
import socket
import stat
import sys
import tempfile
import unittest

from supervisor.compat import as_bytes
from supervisor.compat import as_string
from supervisor.compat import sha1
from supervisor.http import NOT_DONE_YET
from supervisor.tests.base import DummySupervisor
from supervisor.tests.base import PopulatedDummySupervisor
from supervisor.tests.base import TempFileOpen
from supervisor.tests.base import DummyRPCInterfaceFactory
from supervisor.tests.base import DummyPConfig
from supervisor.tests.base import DummyOptions
from supervisor.tests.base import DummyRequest
from supervisor.tests.base import DummyLogger


class HandlerTests:
    def _makeOne(self, supervisord):
        return self._getTargetClass()(supervisord)

    def test_match(self):
        class FakeRequest:
            def __init__(self, uri):
                self.uri = uri

        supervisor = DummySupervisor()
        handler = self._makeOne(supervisor)
        self.assertEqual(handler.match(FakeRequest(handler.path)), True)


class LogtailHandlerTests(HandlerTests, unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import logtail_handler
        return logtail_handler

    def test_handle_request_stdout_logfile_none(self):
        options = DummyOptions()
        pconfig = DummyPConfig(options, 'process1', '/bin/process1', priority=1,
                               stdout_logfile='/tmp/process1.log')
        supervisord = PopulatedDummySupervisor(options, 'process1', pconfig)
        handler = self._makeOne(supervisord)
        request = DummyRequest('/logtail/process1', None, None, None)
        handler.handle_request(request)
        self.assertEqual(request._error, 410)

    def test_handle_request_stdout_logfile_missing(self):
        options = DummyOptions()
        pconfig = DummyPConfig(options, 'foo', 'foo', 'it/is/missing')
        supervisord = PopulatedDummySupervisor(options, 'foo', pconfig)
        handler = self._makeOne(supervisord)
        request = DummyRequest('/logtail/foo', None, None, None)
        handler.handle_request(request)
        self.assertEqual(request._error, 410)

    def test_handle_request(self):
        fd, tfilename = tempfile.mkstemp()
        try:
            options = DummyOptions()
            pconfig = DummyPConfig(options, 'foo', 'foo', stdout_logfile=tfilename)
            supervisord = PopulatedDummySupervisor(options, 'foo', pconfig)
            handler = self._makeOne(supervisord)
            request = DummyRequest('/logtail/foo', None, None, None)
            handler.handle_request(request)
            self.assertEqual(request._error, None)
            from supervisor.medusa import http_date
            self.assertEqual(request.headers['Last-Modified'],
                             http_date.build_http_date(os.stat(tfilename)[stat.ST_MTIME]))
            self.assertEqual(request.headers['Content-Type'], 'text/plain')
            self.assertEqual(len(request.producers), 1)
            self.assertEqual(request._done, True)
        finally:
            os.close(fd)


class MainLogTailHandlerTests(HandlerTests, unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import mainlogtail_handler
        return mainlogtail_handler

    def test_handle_request_stdout_logfile_none(self):
        supervisor = DummySupervisor()
        handler = self._makeOne(supervisor)
        request = DummyRequest('/mainlogtail', None, None, None)
        handler.handle_request(request)
        self.assertEqual(request._error, 410)

    def test_handle_request_stdout_logfile_missing(self):
        supervisor = DummySupervisor()
        supervisor.options.logfile = '/not/there'
        request = DummyRequest('/mainlogtail', None, None, None)
        handler = self._makeOne(supervisor)
        handler.handle_request(request)
        self.assertEqual(request._error, 410)

    def test_handle_request(self):
        supervisor = DummySupervisor()
        fd, tfilename = tempfile.mkstemp()
        try:
            supervisor.options.logfile = tfilename
            handler = self._makeOne(supervisor)
            request = DummyRequest('/mainlogtail', None, None, None)
            handler.handle_request(request)
            self.assertEqual(request._error, None)
            from supervisor.medusa import http_date
            self.assertEqual(request.headers['Last-Modified'],
                             http_date.build_http_date(os.stat(tfilename)[stat.ST_MTIME]))
            self.assertEqual(request.headers['Content-Type'], 'text/plain')
            self.assertEqual(len(request.producers), 1)
            self.assertEqual(request._done, True)
        finally:
            os.close(fd)

class TailFProducerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import tail_f_producer
        return tail_f_producer

    def _makeOne(self, request, filename, head):
        return self._getTargetClass()(request, filename, head)

    def test_handle_more(self):
        request = DummyRequest('/logtail/foo', None, None, None)
        from supervisor import http
        with TempFileOpen() as tmpfile:
            # test 1
            tmpfile.write(b'a' * 80)
            tmpfile.flush()
            producer = self._makeOne(request, tmpfile.name, 80)
            result = producer.more()
            self.assertEqual(result, b'a' * 80)

            # test 2
            tmpfile.write(b'b' * 100)
            tmpfile.flush()
            result = producer.more()
            self.assertEqual(result, b'b' * 100)

            result = producer.more()
            self.assertEqual(result, http.NOT_DONE_YET)
            tmpfile.truncate(0)
            tmpfile.flush()

            result = producer.more()
            self.assertEqual(result, '==> File truncated <==\n')

    def test_handle_more_fd_closed(self):
        request = DummyRequest('/logtail/foo', None, None, None)
        with TempFileOpen() as tmpfile:

            tmpfile.write(as_bytes('a' * 80))
            tmpfile.flush()

            producer = self._makeOne(request, tmpfile.name, 80)
            producer.close()
            producer.more()

            result = producer.more()
            self.assertEqual(result, NOT_DONE_YET)

    def test_handle_more_follow_file_recreated(self):
        request = DummyRequest('/logtail/foo', None, None, None)
        tmpfile = TempFileOpen()
        try:
            tmpfile.write(as_bytes('a' * 80))
            tmpfile.flush()

            producer = self._makeOne(request, tmpfile.name, 80)
            result = producer.more()

            self.assertEqual(result, b'a' * 80)

            # in windows open files need to be closed
            tmpfile.close()

            tmpfile = open(tmpfile.name, 'wb')
            try:
                tmpfile.write(as_bytes(b'b' * 80))
                tmpfile.flush()
                result = producer.more()
            finally:
                tmpfile.close()
                os.remove(tmpfile.name)
        finally:
            tmpfile.close()
        self.assertEqual(result, b'b' * 80)

    def test_handle_more_follow_file_gone(self):
        request = DummyRequest('/logtail/foo', None, None, None)
        with TempFileOpen(mode='wb') as tmpfile:
            tmpfile.write(b'a' * 80)

            producer = self._makeOne(request, tmpfile.name, 80)
            result = producer.more()
            self.assertEqual(result, b'a' * 80)

            with open(tmpfile.name, 'wb') as tmpfile:
                tmpfile.write(b'b' * 80)

            result = producer.more()  # should open in new file
            self.assertEqual(result, b'b' * 80)


class DeferringChunkedProducerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import deferring_chunked_producer
        return deferring_chunked_producer

    def _makeOne(self, producer, footers=None):
        return self._getTargetClass()(producer, footers)

    def test_more_not_done_yet(self):
        wrapped = DummyProducer(NOT_DONE_YET)
        producer = self._makeOne(wrapped)
        self.assertEqual(producer.more(), NOT_DONE_YET)

    def test_more_string(self):
        wrapped = DummyProducer(b'hello')
        producer = self._makeOne(wrapped)
        self.assertEqual(producer.more(), b'5\r\nhello\r\n')

    def test_more_nodata(self):
        wrapped = DummyProducer()
        producer = self._makeOne(wrapped, footers=[b'a', b'b'])
        self.assertEqual(producer.more(), b'0\r\na\r\nb\r\n\r\n')

    def test_more_nodata_footers(self):
        wrapped = DummyProducer(b'')
        producer = self._makeOne(wrapped, footers=[b'a', b'b'])
        self.assertEqual(producer.more(), b'0\r\na\r\nb\r\n\r\n')

    def test_more_nodata_nofooters(self):
        wrapped = DummyProducer(b'')
        producer = self._makeOne(wrapped)
        self.assertEqual(producer.more(), b'0\r\n\r\n')

    def test_more_noproducer(self):
        producer = self._makeOne(None)
        self.assertEqual(producer.more(), b'')


class DeferringCompositeProducerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import deferring_composite_producer
        return deferring_composite_producer

    def _makeOne(self, producers):
        return self._getTargetClass()(producers)

    def test_more_not_done_yet(self):
        wrapped = DummyProducer(NOT_DONE_YET)
        producer = self._makeOne([wrapped])
        self.assertEqual(producer.more(), NOT_DONE_YET)

    def test_more_string(self):
        wrapped1 = DummyProducer('hello')
        wrapped2 = DummyProducer('goodbye')
        producer = self._makeOne([wrapped1, wrapped2])
        self.assertEqual(producer.more(), 'hello')
        self.assertEqual(producer.more(), 'goodbye')
        self.assertEqual(producer.more(), b'')

    def test_more_nodata(self):
        wrapped = DummyProducer()
        producer = self._makeOne([wrapped])
        self.assertEqual(producer.more(), b'')


class DeferringGlobbingProducerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import deferring_globbing_producer
        return deferring_globbing_producer

    def _makeOne(self, producer, buffer_size=1 << 16):
        return self._getTargetClass()(producer, buffer_size)

    def test_more_not_done_yet(self):
        wrapped = DummyProducer(NOT_DONE_YET)
        producer = self._makeOne(wrapped)
        self.assertEqual(producer.more(), NOT_DONE_YET)

    def test_more_string(self):
        wrapped = DummyProducer('hello', 'there', 'guy')
        producer = self._makeOne(wrapped, buffer_size=1)
        self.assertEqual(producer.more(), b'hello')

        wrapped = DummyProducer('hello', 'there', 'guy')
        producer = self._makeOne(wrapped, buffer_size=50)
        self.assertEqual(producer.more(), b'hellothereguy')

    def test_more_nodata(self):
        wrapped = DummyProducer()
        producer = self._makeOne(wrapped)
        self.assertEqual(producer.more(), b'')


class DeferringHookedProducerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import deferring_hooked_producer
        return deferring_hooked_producer

    def _makeOne(self, producer, function):
        return self._getTargetClass()(producer, function)

    def test_more_not_done_yet(self):
        wrapped = DummyProducer(NOT_DONE_YET)
        producer = self._makeOne(wrapped, None)
        self.assertEqual(producer.more(), NOT_DONE_YET)

    def test_more_string(self):
        wrapped = DummyProducer('hello')
        L = []

        def callback(bytes):
            L.append(bytes)

        producer = self._makeOne(wrapped, callback)
        self.assertEqual(producer.more(), 'hello')
        self.assertEqual(L, [])
        producer.more()
        self.assertEqual(L, [5])

    def test_more_nodata(self):
        wrapped = DummyProducer()
        L = []

        def callback(bytes):
            L.append(bytes)

        producer = self._makeOne(wrapped, callback)
        self.assertEqual(producer.more(), b'')
        self.assertEqual(L, [0])

    def test_more_noproducer(self):
        producer = self._makeOne(None, None)
        self.assertEqual(producer.more(), b'')


class Test_deferring_http_request(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import deferring_http_request
        return deferring_http_request

    def _makeOne(
            self,
            channel=None,
            req='GET / HTTP/1.0',
            command='GET',
            uri='/',
            version='1.0',
            header=(),
    ):
        return self._getTargetClass()(
            channel, req, command, uri, version, header
        )

    def _makeChannel(self):
        class Channel:
            closed = False

            def close_when_done(self):
                self.closed = True

            def push_with_producer(self, producer):
                self.producer = producer

        return Channel()

    def test_done_http_10_nokeepalive(self):
        channel = self._makeChannel()
        inst = self._makeOne(channel=channel, version='1.0')
        inst.done()
        self.assertTrue(channel.closed)

    def test_done_http_10_keepalive_no_content_length(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.0',
            header=['Connection: Keep-Alive'],
        )

        inst.done()
        self.assertTrue(channel.closed)

    def test_done_http_10_keepalive_and_content_length(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.0',
            header=['Connection: Keep-Alive'],
        )
        inst.reply_headers['Content-Length'] = 1
        inst.done()
        self.assertEqual(inst['Connection'], 'Keep-Alive')
        self.assertFalse(channel.closed)

    def test_done_http_11_connection_close(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.1',
            header=['Connection: close']
        )
        inst.done()
        self.assertTrue(channel.closed)

    def test_done_http_11_unknown_transfer_encoding(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.1',
        )
        inst.reply_headers['Transfer-Encoding'] = 'notchunked'
        inst.done()
        self.assertTrue(channel.closed)

    def test_done_http_11_chunked_transfer_encoding(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.1',
        )
        inst.reply_headers['Transfer-Encoding'] = 'chunked'
        inst.done()
        self.assertFalse(channel.closed)

    def test_done_http_11_use_chunked(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.1',
        )
        inst.use_chunked = True
        inst.done()
        self.assertTrue('Transfer-Encoding' in inst)
        self.assertFalse(channel.closed)

    def test_done_http_11_wo_content_length_no_te_no_use_chunked_close(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version='1.1',
        )
        inst.use_chunked = False
        inst.done()
        self.assertTrue(channel.closed)

    def test_done_http_09(self):
        channel = self._makeChannel()
        inst = self._makeOne(
            channel=channel,
            version=None,
        )
        inst.done()
        self.assertTrue(channel.closed)


class EncryptedDictionaryAuthorizedTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import encrypted_dictionary_authorizer
        return encrypted_dictionary_authorizer

    def _makeOne(self, dict):
        return self._getTargetClass()(dict)

    def test_authorize_baduser(self):
        authorizer = self._makeOne({})
        self.assertFalse(authorizer.authorize(('foo', 'bar')))

    def test_authorize_gooduser_badpassword(self):
        authorizer = self._makeOne({'foo': 'password'})
        self.assertFalse(authorizer.authorize(('foo', 'bar')))

    def test_authorize_gooduser_goodpassword(self):
        authorizer = self._makeOne({'foo': 'password'})
        self.assertTrue(authorizer.authorize(('foo', 'password')))

    def test_authorize_gooduser_goodpassword_with_colon(self):
        authorizer = self._makeOne({'foo': 'pass:word'})
        self.assertTrue(authorizer.authorize(('foo', 'pass:word')))

    def test_authorize_gooduser_badpassword_sha(self):
        password = '{SHA}' + sha1(as_bytes('password')).hexdigest()
        authorizer = self._makeOne({'foo': password})
        self.assertFalse(authorizer.authorize(('foo', 'bar')))

    def test_authorize_gooduser_goodpassword_sha(self):
        password = '{SHA}' + sha1(as_bytes('password')).hexdigest()
        authorizer = self._makeOne({'foo': password})
        self.assertTrue(authorizer.authorize(('foo', 'password')))


class SupervisorAuthHandlerTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import supervisor_auth_handler
        return supervisor_auth_handler

    def _makeOne(self, dict, handler):
        return self._getTargetClass()(dict, handler)

    def test_ctor(self):
        handler = self._makeOne({'a': 1}, None)
        from supervisor.http import encrypted_dictionary_authorizer
        self.assertEqual(handler.authorizer.__class__,
                         encrypted_dictionary_authorizer)

    def test_handle_request_authorizes_good_credentials(self):
        request = DummyRequest('/logtail/process1', None, None, None)
        encoded = base64.b64encode(as_bytes("user:password"))
        request.header = ["Authorization: Basic %s" % as_string(encoded)]
        handler = DummyHandler()
        auth_handler = self._makeOne({'user': 'password'}, handler)
        auth_handler.handle_request(request)
        self.assertTrue(handler.handled_request)

    def test_handle_request_authorizes_good_password_with_colon(self):
        request = DummyRequest('/logtail/process1', None, None, None)
        # password contains colon
        encoded = base64.b64encode(as_bytes("user:pass:word"))
        request.header = ["Authorization: Basic %s" % as_string(encoded)]
        handler = DummyHandler()
        auth_handler = self._makeOne({'user': 'pass:word'}, handler)
        auth_handler.handle_request(request)
        self.assertTrue(handler.handled_request)

    def test_handle_request_does_not_authorize_bad_credentials(self):
        request = DummyRequest('/logtail/process1', None, None, None)
        encoded = base64.b64encode(as_bytes("wrong:wrong"))
        request.header = ["Authorization: Basic %s" % as_string(encoded)]
        handler = DummyHandler()
        auth_handler = self._makeOne({'user': 'password'}, handler)
        auth_handler.handle_request(request)
        self.assertFalse(handler.handled_request)

class LogWrapperTests(unittest.TestCase):
    def _getTargetClass(self):
        from supervisor.http import LogWrapper
        return LogWrapper

    def _makeOne(self, logger):
        return self._getTargetClass()(logger)

    def test_strips_trailing_newlines_from_msgs(self):
        logger = DummyLogger()
        log_wrapper = self._makeOne(logger)
        log_wrapper.log("foo\n")
        logdata = logger.data
        self.assertEqual(len(logdata), 1)
        self.assertEqual(logdata[0], "foo")

    def test_logs_msgs_with_error_at_error_level(self):
        logger = DummyLogger()
        log_wrapper = self._makeOne(logger)
        errors = []
        logger.error = errors.append
        log_wrapper.log("Server Error")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "Server Error")

    def test_logs_other_messages_at_trace_level(self):
        logger = DummyLogger()
        log_wrapper = self._makeOne(logger)
        traces = []
        logger.trace = traces.append
        log_wrapper.log("GET /")
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0], "GET /")

class TopLevelFunctionTests(unittest.TestCase):
    def _make_http_servers(self, sconfigs):
        options = DummyOptions()
        options.server_configs = sconfigs
        options.rpcinterface_factories = [('dummy', DummyRPCInterfaceFactory, {})]
        supervisord = DummySupervisor()
        from supervisor.http import make_http_servers
        servers = make_http_servers(options, supervisord)
        try:
            for config, s in servers:
                s.close()
                socketfile = config.get('file')
                if socketfile is not None:
                    os.unlink(socketfile)
        finally:
            from asyncore import socket_map
            socket_map.clear()
        return servers

    def test_make_http_servers_socket_type_error(self):
        config = {'family': 999, 'host': 'localhost', 'port': 17735,
                  'username': None, 'password': None,
                  'section': 'inet_http_server'}
        try:
            self._make_http_servers([config])
            self.fail('nothing raised')
        except ValueError as exc:
            self.assertEqual(exc.args[0], 'Cannot determine socket type 999')

    def test_make_http_servers_noauth(self):
        inet = {'family': socket.AF_INET, 'host': 'localhost', 'port': 17735,
                'username': None, 'password': None, 'section': 'inet_http_server'}
        servers = self._make_http_servers([inet])
        self.assertEqual(len(servers), 1)

        inetdata = servers[0]
        self.assertEqual(inetdata[0], inet)
        server = inetdata[1]
        idents = [
            'Supervisor XML-RPC Handler',
            'Logtail HTTP Request Handler',
            'Main Logtail HTTP Request Handler',
            'Supervisor Web UI HTTP Request Handler',
            'Default HTTP Request Handler'
        ]
        self.assertEqual([x.IDENT for x in server.handlers], idents)

    def test_make_http_servers_withauth(self):
        inet = {'family': socket.AF_INET, 'host': 'localhost', 'port': 17736,
                'username': 'username', 'password': 'password',
                'section': 'inet_http_server'}
        servers = self._make_http_servers([inet])
        self.assertEqual(len(servers), 1)
        from supervisor.http import supervisor_auth_handler
        for config, server in servers:
            for handler in server.handlers:
                self.assertTrue(isinstance(handler, supervisor_auth_handler),
                                handler)


class DummyHandler:
    def __init__(self):
        self.handled_request = False

    def handle_request(self, request):
        self.handled_request = True


class DummyProducer:
    def __init__(self, *data):
        self.data = list(data)

    def more(self):
        if self.data:
            return self.data.pop(0)
        else:
            return b''


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
