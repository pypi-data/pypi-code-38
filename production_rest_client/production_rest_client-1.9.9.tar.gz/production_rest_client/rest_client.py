# coding=utf-8
# pylint: disable=wrong-import-position, relative-import
import sys
import os
import requests
sys.path.append(os.path.join(os.path.dirname(__file__)))
from resources.test_resource import TestResource
from resources.operation_resource import OperationResource
from resources.state_resource import StateResource
from resources.remote_resource import RemoteResource


class RestClient(object):

    def __init__(self, host, port=5000, time_out=5):
        __session = requests.Session()
        self.test = TestResource(host, port, __session, time_out=time_out)
        self.operation = OperationResource(host, port, __session, time_out=time_out)
        self.state = StateResource(host, port, __session, time_out=time_out)
        self.remote = RemoteResource(host, port, self.test, self.state)

if __name__ == '__main__':
    RC = RestClient("172.29.130.138", time_out=5)
    # print(RC.test.run("fio", "async"))
    print(RC.test.get_async_result("TQtRRRdCTe"))
    print(RC.test.get_test_lists("fio"))
    # #print(RC.state.get_state())
    # #print(RC.test_suite.get_test_lists("fio"))
    # # print(RC.test_case.list("fio"))
    # # print(RC.remote.run("test_fio_windows:TestFioWindows.test_rand_mix_rw_70_30", "async"))
    # print(RC.test_case.get_async_result("9cd1r0nbc2"))
    # print(RC.test_suite.get_async_result("9cd1r0nbc2"))
    # # print(RC.test_case.stop_tests())
