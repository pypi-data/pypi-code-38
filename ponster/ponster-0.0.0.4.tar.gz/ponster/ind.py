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
from multiprocessing import Process
import structlog
from simplejson import dumps
from google.protobuf.json_format import MessageToJson

import openolt_pb2_grpc
import openolt_pb2
from confluent_kafka import Producer


log = structlog.get_logger()


class Indications(object):
    def __init__(self, host_and_port, broker='localhost:9092'):
        super(Indications, self).__init__()
        log.debug('Southbound Grpc Rx')
        self.host_and_port = host_and_port
        self.broker = broker

        try:
            # Start indications_process
            self.indications_process = Process(
                target=self.process_indications,
                args=(broker, host_and_port,))
        except Exception as e:
            log.exception('Indications initialization failed', e=e)
        else:
            log.debug('Indications initialized')

    def start(self):
        try:
            # Start indications_process
            log.debug('openolt grpc starting')
            self.indications_process.start()
        except Exception as e:
            log.exception('indication start failed', e=e)
        else:
            log.debug('openolt grpc started')

        try:
            self.indications_process.join()
        except KeyboardInterrupt:
            self.indications_process.terminate()

    def process_indications(self, host_and_port, broker):
        channel = grpc.insecure_channel(host_and_port)
        stub = openolt_pb2_grpc.OpenoltStub(channel)
        stream = stub.EnableIndication(openolt_pb2.Empty())

        default_topic = 'openolt.ind-{}'.format(host_and_port.split(':')[0])
        pktin_topic = 'openolt.pktin-{}'.format(host_and_port.split(':')[0])

        conf = {'bootstrap.servers': broker}

        p = Producer(**conf)

        while True:
            try:
                # get the next indication from olt
                print('waiting for indication...')
                ind = next(stream)
            except Exception as e:
                log.warn('openolt grpc connection lost', error=e)
                '''
                ind = openolt_pb2.Indication()
                ind.olt_ind.oper_state = 'down'
                kafka_send_pb(default_topic, ind)
                break
                '''
            else:
                sys.stdout.write(str(ind))
                if ind.HasField('pkt_ind'):
                    p.produce(pktin_topic,
                              dumps(MessageToJson(
                                  ind, including_default_value_fields=True)))
                else:
                    p.produce(default_topic,
                              dumps(MessageToJson(
                                  ind, including_default_value_fields=True)))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        sys.stderr.write(
            'Usage: %s <kafka-broker> <olt hostname or ip>\n\n' % sys.argv[0])
        sys.exit(1)

    broker = sys.argv[1]
    host_and_port = sys.argv[2]

    Indications(broker, host_and_port).start()
