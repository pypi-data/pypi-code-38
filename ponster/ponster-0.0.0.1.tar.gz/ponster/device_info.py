#  Copyright 2019 Shad Ansari
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
import grpc
import time
from multiprocessing import Process
import structlog

import openolt_pb2_grpc
import openolt_pb2


log = structlog.get_logger()


class DeviceInfo(object):
    def __init__(self, host_and_port, broker='localhost:9092'):
        super(DeviceInfo, self).__init__()
        self.host_and_port = host_and_port
        self.broker = broker
        self.device_info = None

        try:
            # Start indications_process
            self.process = Process(
                target=self.main,
                args=(host_and_port, broker,))
        except Exception as e:
            log.exception('Olt initialization failed', e=e)

    def start(self):
        try:
            self.process.start()
        except Exception as e:
            log.exception('Olt start failed', e=e)

        try:
            self.process.join()
        except KeyboardInterrupt:
            self.process.terminate()

    def main(self, host_and_port, broker):
        channel = grpc.insecure_channel(self.host_and_port)
        self.stub = openolt_pb2_grpc.OpenoltStub(channel)

        self.get_device_info()  # block

    def get_device_info(self):
        # timeout = 60*60
        timeout = 10
        delay = 1
        exponential_back_off = False
        while True:
            try:
                self.device_info = self.stub.GetDeviceInfo(openolt_pb2.Empty())
                if __name__ == '__main__':
                    sys.stdout.write(str(self.device_info))
                break
            except Exception as e:
                if delay > timeout:
                    log.error("Timed out, giving up...")
                    return
                else:
                    log.info("Retrying %s in %ds: %s" % (self.host_and_port,
                                                         delay, repr(e)))
                    time.sleep(delay)
                    if exponential_back_off:
                        delay += delay
                    else:
                        delay += 1


if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stderr.write(
            'Usage: %s <olt ip:port>\n\n' % sys.argv[0])
        sys.exit(1)

    olt_ip = sys.argv[1]

    DeviceInfo(olt_ip).start()
