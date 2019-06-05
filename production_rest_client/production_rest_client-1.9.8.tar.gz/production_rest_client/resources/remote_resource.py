# coding=utf-8
# pylint: disable=import-error, broad-except
import time
from resources.models.remoter import RemoteCtrl


class RemoteResource(object):

    def __init__(self, host, port, session, state):
        self.host = host
        self.port = port
        self.testcase = session
        self.state = state
        cfg_file = './comConfig.yaml'
        self.remote = RemoteCtrl(host, ini=cfg_file)

    def list(self, filter_):
        '''
        get all test cases
        '''
        pass

    def run(self, test_case, mode="async"):
        """
        :param test_case: type string, test case name
        :param  mode: sync or async, run test case
        :return: type bool, return test case run result
        """
        for _ in range(5000):
            #ret = self.testcase.run(test_case, mode)
            #print(ret)
            #if self.check_test_status(ret['data'][0]):
            #    print('test failed')
            #    return 1
            ret = self.remote.reset_remote()
            print(ret)
            if ret['result']:
                print(ret['msg'])
                return 1
            if self.check_target_status():
                print('failed to connect server')
                return 1
        return 0

    def check_test_status(self, key):
        '''
        check test state through API
        '''
        while True:
            ret = self.testcase.get_async_result(key)
            print(ret)
            if 'state' in ret:
                if ret['state'] == 1:
                    return 0
                if ret['state'] not in [1, 2, 3, 13]:
                    return 1
            time.sleep(5)


    def check_target_status(self):
        '''
        check the target machine state through API
        '''
        fail_count = 1
        while fail_count <= 30:
            ret = self.state.get_state()
            if 'state' in ret:
                stat = ret['state']
                if stat == 1:
                    print("Server is Running\nIP:%s"%self.host)
                    return 0
                else:
                    print("Failed to connect Server IP:%s\n"%self.host)
                    fail_count += 1
                time.sleep(5)
        return 1
