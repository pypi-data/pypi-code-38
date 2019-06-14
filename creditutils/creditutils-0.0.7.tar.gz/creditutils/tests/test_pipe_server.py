'''
Created on 2015年1月13日

@author: caifh
'''
import unittest
import creditutils.pipe_util as pipe
import time


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_pipe_main():
    client = pipe.ReadClient()
    if client.Connect():
        consumer = pipe.Consumer()
        client.SetReceiver(consumer.Process)
        client.Receive()


def test_server():
    pipe.CreateServer()


#     time.sleep(10)

def test_main():
    #     test_pipe_main()
    test_server()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()

    print('to the end')
