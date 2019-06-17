import unittest
import sys
import os

from thread_testing import get_num_non_dummy_threads, wait_till_joined, wait_till_condition

from pynetworking.Communication_client import ServerCommunicator, MultiServerCommunicator, ServerFunctions
from pynetworking.Communication_server import ClientManager, ClientFunctions, ClientCommunicator, MetaClientManager
from pynetworking.Communication_general import to_server_id
import pynetworking.Communication_general
from pynetworking.Logging import logger

from pynetworking.tests.example_functions import DummyPerson, DummyServerCommunicator, DummyClientCommunicator, \
    DummyMultiServerCommunicator

dummy_address = ("localhost", 5000)
server_address = ("0.0.0.0", 5000)

logger.setLevel(10)


class CommunicationTestCase(unittest.TestCase):
    def tearDown(self):
        DummyServerCommunicator.close_connection()
        MultiServerCommunicator.close_all_connections()
        MetaClientManager.tear_down()

    def setUp(self):
        DummyMultiServerCommunicator.close_all_connections()
        DummyServerCommunicator.close_connection()


class StdOutEqualizer:

    def __init__(self, test_case, expected):
        self.test_case: CommunicationTestCase = test_case
        self.expected = expected
        self.original = sys.stdout
        self.file_path = os.path.join(os.path.split(__file__)[0], "std_out.txt")

    def __enter__(self):
        self.original = sys.stdout
        sys.stdout = open(self.file_path, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.original
        with open(self.file_path, "r") as std_out:
            self.test_case.assertEqual(self.expected, std_out.read().strip())


class TestConnecting(CommunicationTestCase):

    def setUp(self):
        DummyServerCommunicator._exchanged_keys = False

    def test_single_client_connect(self):
        DummyServerCommunicator.connect(dummy_address, timeout=0)
        self.assertEqual(DummyServerCommunicator.remote_functions.__getattr__("_connector"), DummyServerCommunicator)
        self.assertEqual(DummyServerCommunicator.remote_functions().__getattr__("_connector"), DummyServerCommunicator)
        self.assertEqual(DummyServerCommunicator.remote_functions, DummyServerCommunicator.remote_functions())

    def test_multi_client_connect(self):
        DummyMultiServerCommunicator(0).connect(dummy_address, timeout=0)
        self.assertIsInstance(DummyMultiServerCommunicator(0).remote_functions.__getattr__("_connector"),
                              DummyMultiServerCommunicator)
        DummyMultiServerCommunicator(1).connect(dummy_address, timeout=0)
        self.assertIsInstance(DummyMultiServerCommunicator(1).remote_functions.__getattr__("_connector"),
                              DummyMultiServerCommunicator)

    def test_single_client(self):
        with ClientManager(server_address, DummyClientCommunicator) as listener:
            wait_till_condition(lambda : False is True, timeout=2)
            DummyServerCommunicator.connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 1, timeout=1)

            self.assertEqual(len(listener.clients), 1)
            self.assertEqual(get_num_non_dummy_threads(), 4)  # Main, listener, client_communicator, server_communicator
            self.assertEqual(listener.clients[to_server_id(0)].communicator._socket_connection.getpeername(),
                             DummyServerCommunicator.communicator._socket_connection.getsockname())
            DummyServerCommunicator.close_connection()
            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=1)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=1)
            # wait_till_condition(lambda: get_num_non_dummy_threads() == 2)

            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener, timeout=1)

        self.assertEqual(get_num_non_dummy_threads(), 1)

    def test_multiple_clients(self):
        pynetworking.Communication_general.set_encrypted_communication(False)
        with ClientManager(server_address, DummyClientCommunicator) as listener:
            DummyMultiServerCommunicator(0).connect(dummy_address)
            DummyMultiServerCommunicator(1).connect(dummy_address)

            wait_till_condition(lambda: len(listener.clients) == 2, timeout=2)

            self.assertEqual(len(listener.clients), 2)

            self.assertEqual(get_num_non_dummy_threads(), 6)
            # Main, listener, 2 * client_communicator, 2 * server_communicator
            self.assertEqual(listener.clients[to_server_id(0)].communicator._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(0).communicator._socket_connection.getsockname())
            self.assertEqual(listener.clients[to_server_id(1)].communicator._socket_connection.getpeername(),
                             DummyMultiServerCommunicator(1).communicator._socket_connection.getsockname())

            DummyMultiServerCommunicator(0).close_connection()
            DummyMultiServerCommunicator(1).close_connection()

            wait_till_joined(DummyMultiServerCommunicator(0).communicator, timeout=2)
            wait_till_joined(DummyMultiServerCommunicator(1).communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients.values()) == 0, timeout=2)
            self.assertEqual(get_num_non_dummy_threads(), 2)  # Main, listener
        wait_till_joined(listener, timeout=1)

        self.assertEqual(get_num_non_dummy_threads(), 1)
        pynetworking.Communication_general.set_encrypted_communication(True)

    def test_offline_server(self):
        connected = DummyServerCommunicator.connect(dummy_address, timeout=0)
        self.assertEqual(get_num_non_dummy_threads(), 1)
        self.assertEqual(connected, False)

    def test_server_turn_on(self):
        DummyServerCommunicator.connect(dummy_address, blocking=False)
        with ClientManager(server_address, DummyClientCommunicator) as listener:
            wait_till_condition(lambda: DummyServerCommunicator._exchanged_keys is True, timeout=4)
            self.assertEqual(len(listener.clients), 1)
            self.assertEqual(True, DummyServerCommunicator._exchanged_keys)
            DummyServerCommunicator.close_connection()
            wait_till_joined(DummyServerCommunicator.communicator, timeout=2)
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients), 0)
        self.assertEqual(get_num_non_dummy_threads(), 1)

    def test_listener_clients(self):
        with ClientManager(server_address, DummyClientCommunicator) as listener:
            self.assertEqual(len(listener.clients.values()), 0)
            DummyServerCommunicator.connect(dummy_address)
            wait_till_condition(lambda: len(listener.clients) == 1, timeout=2)
            self.assertEqual(len(listener.clients.values()), 1)
            DummyServerCommunicator.close_connection()
            wait_till_condition(lambda: len(listener.clients) == 0, timeout=2)
            self.assertEqual(len(listener.clients.values()), 0)


class TestCommunicating(CommunicationTestCase):

    def helper_test_func(self, func, args: tuple, expected_ret):
        with ClientManager(server_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)
            try:
                ret_value = func(*args)
                self.assertEqual(expected_ret, ret_value)
            except TimeoutError:
                self.fail("TimeoutError")

    # Error cases
    def test_functions_no_connection(self):
        self.assertRaises(ConnectionError, DummyServerCommunicator.remote_functions(timeout=0).dummy_no_arg_no_ret)

    def test_functions_timeout(self):
        # May fail if packets are handled at server is implemented
        with ClientManager(dummy_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)
            self.assertRaises(TimeoutError, DummyServerCommunicator.remote_functions(timeout=0).dummy_no_arg_no_ret)

    # Succeed cases
    def test_no_arg_no_ret(self):
        with StdOutEqualizer(self, "no_arg_no_ret() called"):
            self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).no_arg_no_ret,
                                  tuple(),
                                  None)

    def test_no_arg_ret(self):
        with StdOutEqualizer(self, "no_arg_ret() called"):
            self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).no_arg_ret,
                                  tuple(),
                                  True)

    def test_immutable_args_ret(self):
        name = "Anne"
        age = 78
        children = ("Tom", "Pia")
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).immutable_args_ret,
                              (name, age, children),
                              f"{name} is {age} old and has {len(children)}: {children}")

    def test_args_ret_object(self):
        name = "Anne"
        age = 78
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).args_ret_object,
                              (name, age),
                              DummyPerson(name, age))

    def test_class_args_ret(self):
        name = "Anne"
        age = 78
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).class_args_ret,
                              (DummyPerson(name, age),),
                              (name, age))

    def test_huge_args_huge_ret(self):
        arg1 = "Text" * 1200
        arg2 = DummyPerson("John", -9100)
        arg3 = "End"
        args = (arg1, arg2, arg3)
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).huge_args_huge_ret,
                              args,
                              args)

    def test_small_file(self):
        import os
        file_path = os.path.join(os.path.split(__file__)[0], "std_out.txt")
        destination_path = os.path.join(os.path.split(__file__)[0], "new_file.txt")
        with ClientManager(server_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)
            file = DummyServerCommunicator.remote_functions().get_file(file_path, destination_path)
            self.assertEqual(file.src_path, file_path)
            self.assertEqual(file.dst_path, destination_path)
        self.assertEqual(os.path.getsize(file_path), os.path.getsize(destination_path))

    def test_huge_file(self):
        import os
        file_path = os.path.join(os.path.split(__file__)[0], "dummy.txt")
        with open(file_path, "w+") as f:
            for i in range(100):
                f.write("H"*100000)

        destination_path = os.path.join(os.path.split(__file__)[0], "new_file.txt")
        with ClientManager(server_address, DummyClientCommunicator):
            DummyServerCommunicator.connect(dummy_address)
            file = DummyServerCommunicator.remote_functions().get_file(file_path, destination_path)
            self.assertEqual(file.src_path, file_path)
            self.assertEqual(file.dst_path, destination_path)
        self.assertEqual(os.path.getsize(file_path), os.path.getsize(destination_path))

    def test_func_in_func(self):
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).func_in_func,
                              (0,),
                              2)

    def test_many_func_in_func(self):
        self.helper_test_func(DummyServerCommunicator.remote_functions(timeout=2).many_func_in_func,
                              tuple(),
                              120)


if __name__ == '__main__':
    unittest.main()
