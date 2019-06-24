
from Orange.widgets.utils.concurrent import FutureWatcher, ThreadExecutor

from PyQt5.QtCore import pyqtSlot
import concurrent.futures
import zerorpc

SERVER_ADDRESS = "tcp://127.0.0.1:9138"


class RpcClient():

    def __init__(self):
        # Async
        self.executor = ThreadExecutor()
        self.future = None

    def requestData(self, method, callback):
        if self.future is not None:
            # First make sure any pending tasks are cancelled.
            self.future.cancel()
            self.future = None

        self.future = self.executor.submit(self.getData, method)
        # Setup the FutureWatcher to notify us of completion
        self.watcher = FutureWatcher(self.future)
        # by using FutureWatcher we ensure `dataReceived` slot will be
        # called from the main GUI thread by the Qt's event loop
        self.watcher.done.connect(self.rpcDataReceived)
        self.callback = callback


    def getData(self, method):
      c = zerorpc.Client()
      c.connect(SERVER_ADDRESS)
      data = getattr(c, method)();
      return data

    @pyqtSlot(concurrent.futures.Future)
    def rpcDataReceived(self, f):
      self.future = None
      try:
        results = f.result()
        self.callback(results);
      except Exception as ex:
        self.error("Exception occurred during evaluation: {!r}".format(ex))

