import zmqflp_client
import zmqflp_server
import time
from multiprocessing import Process, set_start_method
import socket
import asyncio
import logging
import cbor2
import uuid
import random

SIM_CLIENTS = 10
LEN_TEST_MESSAGE = 10
log_handlers = [logging.StreamHandler()]
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=log_handlers,
    level=logging.DEBUG)


def server_main():
    asyncio.run(server_loop())
    return 0


async def server_loop():
    server = zmqflp_server.ZMQFLPServer(str_port='9001')
    keep_running = True
    while keep_running:
        # handle the "TEST" requests
        (req_object, orig_headers) = await server.receive()
        if req_object is None:
            continue
        elif req_object != "EXIT":
            await server.send(orig_headers, req_object)
        elif req_object == "EXIT":
            logging.info('server exiting...')
            await server.send(orig_headers, "EXITING")
            keep_running = False
    if keep_running is False:
        return


def client_loop(num_of_tests):
    client = zmqflp_client.ZMQFLPClient([socket.gethostbyname(socket.gethostname()) + ':9001'])
    randtag = uuid.uuid4()
    time.sleep(random.randint(1, 6))
    for i in range(num_of_tests):
        test_message = str(["TEST"+str(i)+str(randtag) for i in range(LEN_TEST_MESSAGE)])
        reply = client.send_and_receive(test_message)
        # logging.info(reply)
        # logging.debug('reply: '+str(reply))
        if (len(reply) != len(test_message)) and (reply[-1] != test_message):  # "TEST_OK":
            logging.debug("TEST_FAILURE")
            raise ValueError()


def run_test(num_of_tests):
    client_processes = []
    for j in range(SIM_CLIENTS):
        client_process = Process(target=client_loop, args=(num_of_tests,))
        client_processes.append(client_process)
    [x.start() for x in client_processes]
    [x.join() for x in client_processes]
    logging.debug("ending client send")
    return


def main():
    set_start_method('spawn')
    requests = 30
    logging.debug(">> starting zmq server!")
    server_process = Process(target=server_main, daemon=True)
    server_process.start()
    time.sleep(3.0)

    logging.debug(">> starting zmq freelance protocol test!")
    start = time.time()
    run_test(requests)
    avg_time = ((time.time() - start) / (requests * SIM_CLIENTS))
    logging.debug(">> waiting for server to exit...")
    server_process.join(timeout=1)
    logging.debug("Average RT time (sec): " + str(avg_time))
    return


if __name__ == '__main__':
    main()
