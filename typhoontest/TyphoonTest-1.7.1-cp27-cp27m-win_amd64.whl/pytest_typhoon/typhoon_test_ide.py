import io
import json
import os
import uuid
import winreg
from typing import List, Dict

import zmq
from enum import Enum, unique
from json import JSONEncoder
import pytest


MSG_SEP = "."


def build_msg_type(parent_msg_type, msg_type_name):
    """
    Builds a new message type.

    Args:
        parent_msg_type(str): Parent message.
        msg_type_name(str): Message type name.

    Returns:
        New message type.
    """
    return MSG_SEP.join((parent_msg_type, msg_type_name))


@unique
class MsgType(Enum):
    """ Common types of messages. """
    #
    # This is always first item in every message, used to indicate
    # Typhoon namespace.
    #
    MSG_TYPHOON = "_#tph"

    # Root general namespace
    MSG_GENERAL = build_msg_type(MSG_TYPHOON, "general")

    # General information ,warning and error message types.
    MSG_INFO = build_msg_type(MSG_GENERAL, "info")
    MSG_WARNING = build_msg_type(MSG_GENERAL, "warning")
    MSG_ERROR = build_msg_type(MSG_GENERAL, "error")

    # Typhoon compiler messages.
    MSG_COMP = build_msg_type(MSG_TYPHOON, "compiler")
    MSG_COMP_STARTED = build_msg_type(MSG_COMP, "started")
    MSG_COMP_FINISHED = build_msg_type(MSG_COMP, "finished")
    MSG_COMP_FINISHED_SUCCESS = build_msg_type(MSG_COMP_FINISHED,
                                               "successfully")
    MSG_COMP_FINISHED_INTERRUPTED = build_msg_type(MSG_COMP_FINISHED,
                                                   "interrupted")
    MSG_COMP_FINISHED_ERROR = build_msg_type(MSG_COMP_FINISHED, "error", )
    MSG_COMP_INFO = build_msg_type(MSG_COMP, "info")
    MSG_COMP_INFO_2 = build_msg_type(MSG_COMP, "info_2")
    MSG_COMP_WARNING = build_msg_type(MSG_COMP, "warning")
    MSG_COMP_WARNING_2 = build_msg_type(MSG_COMP, "warning_2")
    MSG_COMP_ERROR = build_msg_type(MSG_COMP, "error")

    MSG_TEST_IDE = build_msg_type(MSG_TYPHOON, "test_ide")
    MSG_TEST_IDE_COLLECTION = build_msg_type(MSG_TEST_IDE, "collection_finish")
    MSG_TEST_IDE_SELECTED = build_msg_type(MSG_TEST_IDE, "selected_tests")
    MSG_TEST_IDE_DESELECTED = build_msg_type(MSG_TEST_IDE, "deselected_tests")
    MSG_TEST_IDE_RUN_REPORT = build_msg_type(MSG_TEST_IDE, "run_report")
    MSG_TEST_IDE_RUN = build_msg_type(MSG_TEST_IDE, "run")
    MSG_TEST_IDE_TEARDOWN_FAILED = build_msg_type(MSG_TEST_IDE, "teardown_failed")
    MSG_TEST_IDE_CAPLOG = build_msg_type(MSG_TEST_IDE, "cap_log")


KwargsDict = Dict[str, object]
Msg = List[bytes]


class IMsgPublisher(object):
    """ Message publishing interface. """

    def publish_msg(self, msg_type, msg, **kwargs):
        """
        Publish message of ``msg_type`` type with accompanying keywords
        arguments collected in ``kwargs`` dictionary.

        Args:
            msg_type(MsgType): Message type enumeration constant.
            msg(str): Actual message string.
            kwargs(dict): Collected keyword arguments.

        Returns:
            None
        """
        raise NotImplementedError()


CoreIdType = str


class Identifiable:
    """ Objects which have id. """

    def __init__(self, *args, **kwargs):
        """ Initialize an object. """
        super(Identifiable, self).__init__(*args, **kwargs)

        self._id = str(uuid.uuid1())

    def get_id(self):
        """ Returns id for object as string. """
        return self._id


class MinimalMsgPublisher(IMsgPublisher, Identifiable):
    """
    Minimal implementation of IMsgPublisher interface.
    It contains only functional zmq underlying sockets to be able to send
    messages. Actual method for publishing messages are abstract.
    """

    def __init__(self, proxy_info):
        """
        Initialize an object.

        Args:
           proxy_info(dict): Message proxy information in dict form.
        """
        super(MinimalMsgPublisher, self).__init__()

        self._pub_ctx = None
        self._pub_sock = None

        self._setup_zmq(pub_port=proxy_info["outbound_port"])
        self._sync_to_proxy(sync_port=proxy_info["sync_port"])

    def _setup_zmq(self, pub_port):
        """
        Setup zmq parts like context and socket.

        Args:
            pub_port(int): Number for outbound proxy port.

        Returns:
            None
        """
        self._pub_ctx = zmq.Context()
        self._pub_sock = self._pub_ctx.socket(zmq.PUB)
        self._pub_sock.setsockopt(zmq.LINGER, 1000)
        self._pub_sock.connect("tcp://localhost:{0}".format(pub_port))

    def _sync_to_proxy(self, sync_port):
        """
        Sync this publisher to messaging proxy.

        Args:
            sync_port(int): Proxy sync port number.

        Returns:
            None
        """
        self._req_sock = self._pub_ctx.socket(zmq.REQ)
        self._req_sock.connect("tcp://localhost:{}".format(sync_port))

        self._req_sock.send(b"Hello")
        poller = zmq.Poller()
        poller.register(self._req_sock, zmq.POLLIN)
        # wait 1 second to receive handshake message
        if poller.poll(1*1000):
            __ = self._req_sock.recv()
        # if handshake message is not received close communication
        else:
            poller.unregister(self._req_sock)
            self._req_sock.setsockopt(zmq.LINGER, 0)
            self._req_sock.close()


class CommonMsgPublisher(MinimalMsgPublisher):
    """
    Implementation of message publisher.
    """

    def __init__(self, proxy_info):
        """
        Initialize an object.

        Args:
           proxy_info(dict): Message proxy information in dict form.
        """
        super(CommonMsgPublisher, self).__init__(proxy_info=proxy_info)

    def publish_msg(self, msg_type, msg, **kwargs):
        """
        See IMsgPublisher.publish_msg docstring.
        Construct message as composed from several parts and sends it
        through socket as multipart message.

        Message format:
             ------------------------------------------------------
            |MsgType enum as str | msg | kwargs json representation|
             ------------------------------------------------------
        """
        msg = (msg_type.value.encode("utf-8"),
               msg.encode("utf-8"),
               json.dumps(kwargs if kwargs else {}).encode("utf-8"))

        self._pub_sock.send_multipart(msg)


class TyphoonTestPlugin(object):
    """
    plugin for pytest
    this plugin sending info about test collecting, running and report of test
    as json objects
    """
    def __init__(self, config):
        try:
            MSG_PROXY_INFO_FILE = config.getoption("--msg_proxy_path")
            # unpack path replace question mark sing with whitespace
            # because commandline arg cannot have whitespace
            MSG_PROXY_INFO_FILE = MSG_PROXY_INFO_FILE.replace("?", " ")
            MSG_PROXY_INFO_FILE = os.path.join(MSG_PROXY_INFO_FILE, 'msgproxy.json')
            with io.open(file=MSG_PROXY_INFO_FILE, mode="r", encoding="utf-8") as proxy_file:
                proxy_info = json.loads(proxy_file.read())
            self.publisher = MyPublisher(proxy_info)
        except:
            self.publisher = DummyPublisher()

    def pytest_runtest_logstart(self, nodeid, location):
        self.publisher.publish_msg(MsgType.MSG_TEST_IDE_RUN, json.dumps(nodeid))

    def pytest_runtest_logreport(self, report):
        self.publisher.publish_msg(MsgType.MSG_TEST_IDE_RUN_REPORT,
                                   json.dumps(report, cls=JsonPyTestReport))

    def pytest_collection_finish(self, session):
        # Maybe pytest_report_collectionfinish is more proper for this
        # but it does not get called when using --collect-only
        self.publisher.publish_msg(MsgType.MSG_TEST_IDE_COLLECTION,
                                   json.dumps(session.items, cls=JsonPyTestCollection))

    def pytest_deselected(self, items):
        self.publisher.publish_msg(MsgType.MSG_TEST_IDE_DESELECTED,
                                   json.dumps(items, cls=JsonPyTestCollection))


class MyPublisher(CommonMsgPublisher):
    """
    custom publisher for sending messages between process
    """

    def __init__(self, proxy_info):
        super(MyPublisher, self).__init__(proxy_info=proxy_info)


class DefaultPublisher(object):
    """
    Interface which dummy publisher expect
    """
    def publish_msg(self, msg_type, msg, **kwargs):\
        pass


class DummyPublisher(DefaultPublisher):
    """
    Msg publisher which does nothing if msg proxy file was not found.
    """
    def __init__(self):
        super(DefaultPublisher, self).__init__()

    def publish_msg(self, msg_type, msg, **kwargs):
        pass



class JsonPyTestCollection(JSONEncoder):
    """
    custom json encoder for encoding pytes obects
    to json objects
    """

    @staticmethod
    def _get_type_name(obj):
        """ Return type (class) name for provided object. """
        return obj.__class__.__name__

    def default(self, o):
        if isinstance(o, pytest.Session):
            return "Root"
        elif isinstance(o, pytest.Function):
            return {
                "__class__": self._get_type_name(o),
                "nodeid": o.nodeid,
                "fspath": o.fspath.strpath,
                "name": o.name,
                "parent": o.parent
            }
        elif isinstance(o, pytest.Class):
            return {
                "__class__": self._get_type_name(o),
                "nodeid": o.nodeid,
                "fspath": o.fspath.strpath,
                "name": o.name,
                "parent": o.parent
            }
        elif isinstance(o, pytest.Instance):
            return {
                "__class__": self._get_type_name(o),
                "nodeid": o.nodeid,
                "fspath": o.fspath.strpath,
                "name": o.name,
                "parent": o.parent.parent
            }

        elif type(o) == pytest.Module:
            return {
                "__class__": self._get_type_name(o),
                "nodeid": o.nodeid,
                "fspath": o.fspath.strpath,
                "name": o.name,
                "parent": o.parent,
            }
        elif type(o) == pytest.Package:
            return {
                "__class__": self._get_type_name(o),
                "nodeid": o.nodeid,
                "fspath": o.fspath.strpath,
                "name": o.name,
                "parent": o.parent,
            }


class JsonPyTestReport(JSONEncoder):
    """
    custom json encoder for encoding pytest report object
    to json objects
    """

    @staticmethod
    def _get_type_name(obj):
        """ Return type (class) name for provided object. """
        return obj.__class__.__name__

    def default(self, o):
        return {
            "__class__": self._get_type_name(o),
            "nodeid": o.nodeid,
            "fspath": o.fspath,
            "duration": o.duration,
            "failed": o.failed,
            "report_text": o.longreprtext,
            "passed": o.passed,
            "skipped": o.skipped,
            "caplog": o.caplog,
            "capstdout": o.capstdout,
            "capstderr": o.capstderr,
            "when": o.when,
        }


def pytest_configure(config):
    """
    configure pytest plugin
    Args:
        config: config of pytest

    Returns:

    """
    # register plugin
    config.pluginmanager.register(TyphoonTestPlugin(config))
