import zmq
import time
from multiprocessing import Process, Manager
from distributed_networking_utilities.zmq_exchange import recv_array

class MultiProcessArrayRecv:

    def __init__(self, n_sender_processes, sender_function, n_thread_workers,
                 bind_addr="tcp://*:5556"):
        self.n_sender_processes = n_sender_processes
        self.sender_function = sender_function
        self.n_thread_workers = n_thread_workers
        self.bind_addr = bind_addr
        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.PAIR)
        self.socket.bind(self.bind_addr)


        self.proc_manager = Manager()
        self.proc_q = self.proc_manager.Queue()
        self.processes = []
        for i in range(self.n_sender_processes):
            self.processes.append(Process(target=self.sender_function,
                                          args=(self.proc_q, i,
                                                self.n_thread_workers)))
            self.processes[-1].start()

    def listen(self):
        while True:
            print("Waiting for requests ...")
            arr, metadata = recv_array(self.socket)
            misc = metadata['misc']

            if 'sent_at' in misc:
                t = time.time() - misc['sent_at']
                print("Received data after {:.2f} secs ...".format(t))

            self.proc_q.put((arr, misc,))
