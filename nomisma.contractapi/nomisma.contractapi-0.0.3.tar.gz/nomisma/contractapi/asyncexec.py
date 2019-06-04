import queue
import concurrent.futures
import sys
import time
from decimal import Decimal
from threading import Thread
from typing import TypeVar, Generic, Dict

ETHER_TO_WAY_FACTOR = Decimal(1e18)

T = TypeVar('T')


class Promise(Generic[T]):
    """
    A typed Future - allows better interaction with IDE's and self-documentation
    """

    def __init__(self, f=None) -> None:
        if f is None:
            self.future = concurrent.futures.Future()
        else:
            self.future = f

    def result(self, timeout=None) -> T:
        return self.future.result(timeout)

    def set_result(self, result: T):
        self.future.set_result(result)

    def set_exception(self, exception):
        self.future.set_exception(exception)

    def done(self) -> bool:
        return self.future.done()


class ReschedulableTask:

    def __init__(self, asyncexec, task, promise: Promise, reschedule_interval):
        self.asyncexec = asyncexec
        self.task = task
        self.promise = promise
        self.execution_time = time.time()
        self.reschedule_interval = reschedule_interval

    def run(self):
        try:
            result = self.task()
            if result is None:
                self.execution_time = time.time() + self.reschedule_interval
                self.asyncexec.reschedule(self)
            else:
                self.promise.set_result(result)
        except:
            self.promise.set_exception(sys.exc_info()[0])


class PeriodicRunnerThread(Thread):
    def __init__(self):
        super().__init__(name='Poller Thread', daemon=True)
        self.queue = queue.Queue()
        self.shutdown = False

    def run(self) -> None:
        while not self.shutdown:
            try:
                runnable = self.queue.get(timeout=1)
                now = time.time()
                if runnable.execution_time > now:
                    time.sleep(runnable.execution_time - now)
                runnable.run()
            except queue.Empty:
                pass

    def add_task(self, task):
        self.queue.put(task)


class AsyncExec:
    def __init__(self, num_threads, poll_interval=1):
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
        self.periodic_runner_thread = PeriodicRunnerThread()
        self.periodic_runner_thread.start()
        self.poll_interval = poll_interval

    def reschedule(self, task):
        self.periodic_runner_thread.add_task(task)

    def poll_until_done(self, task, promise_to_set: Promise) -> Promise:
        task = ReschedulableTask(self, task, promise_to_set, self.poll_interval)
        self.reschedule(task)
        return promise_to_set

    def submit(self, runnable) -> Promise:
        return Promise(self.pool.submit(runnable))

    def shutdown(self):
        self.periodic_runner_thread.shutdown = True
        self.pool.shutdown()


class UnsentTransaction(Generic[T]):
    """
    This class represents a transaction that is not yet sent to the Ethereum network at construction.
    If should either be sent to the network via the send() method,
    or used to build_transaction(), which can be signed and sent separately.

    It's possible to change the caller_account before calling send() or build_transaction()
    """

    def __init__(self, contract_meta, func, pay_ether=None):
        self.web3 = contract_meta.web3
        self.func = func
        self.signer = contract_meta.signer
        self.asyncexec = contract_meta.asyncexec
        self.tx_hash = Promise()
        self.pay_ether = pay_ether

    def _initiate_raw_io(self, promise_to_set: Promise):
        try:
            raw_tx = self.signer.sign(self.build_transaction())
            tx_hash = self.web3.eth.sendRawTransaction(raw_tx)
            self.tx_hash.set_result(tx_hash)
            self.asyncexec.poll_until_done(lambda: self._quick_wait(tx_hash), promise_to_set)
        except:
            promise_to_set.set_exception(sys.exc_info()[0])

    def _quick_wait(self, tx_hash):
        return self.web3.eth.getTransactionReceipt(tx_hash)

    def send(self) -> Promise[T]:
        """
        send the transaction to the network
        :return: A Promise that can wait for the result to come back
        """
        f = Promise()
        if self.signer is None:
            raise TypeError
        self.asyncexec.submit(lambda: self._initiate_raw_io(f))
        return f

    def execute_now(self) -> T:
        return self.send().result()

    def build_transaction(self, gas_estimate: int = None) -> Dict:
        """
        builds a transaction that can then be signed and sent.
        See the web3.py docs for examples.
        tx_dict = unsent_tx.build_transaction()
        key = "0x0..."
        w3.eth.account.signTransaction(tx_dict, key)
        :return: a transaction representing the contract method being called from caller_account
        """
        if gas_estimate is None:
            gas_estimate = self.func.estimateGas() * 3
        return self.func.buildTransaction(self.transact_dict(gas_estimate))

    def transact_dict(self, gas_estimate):
        tx_dict = {'gas': gas_estimate}
        if self.pay_ether is not None:
            tx_dict['value'] = int(self.pay_ether * ETHER_TO_WAY_FACTOR)
        return tx_dict
