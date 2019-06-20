# [start-snippet-1]
import numpy
from functools import partial

import Orange.data
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.data import Domain, DiscreteVariable, ContinuousVariable
from Orange.widgets.utils.concurrent import FutureWatcher, ThreadExecutor

from PyQt5.QtCore import pyqtSlot, Qt
import concurrent.futures
import sys
import zerorpc
import math


class CompletionInput(OWWidget):
    name = "Completion Data Input"
    description = "Completion Data Input"
    icon = "icons/input.svg"
    priority = 10
    predefinedColumns = [ "Stage", "MD start", "MD end", "# of clusters", "Total Proppant", "Total Fluid" ]
    predefinedDomain = Domain(list(map(lambda col: ContinuousVariable.make(col), predefinedColumns)))


    class Outputs:
        data = Output("Completion table", Orange.data.Table)

    want_main_area = False
    wellName = Setting("")
    table =  Orange.data.Table(predefinedDomain)

    def __init__(self):
        super().__init__()
        # GUI
        # gui.lineEdit(self.controlArea, self, "wellName",
        #   box = "Well name",
        #   orientation=Qt.Horizontal,
        #   callback=self.wellNameChanged)
        self.names = self.getWellNames()
        gui.comboBox(self.controlArea, self, "wellName",
          "Well name",
          sendSelectedValue = True,
          items = self.names,
          orientation=Qt.Horizontal,
          callback=self.wellNameChanged)

        gui.button(self.controlArea, self, "Update", callback=self.update)

        # Async
        self.executor = ThreadExecutor()
        self.future = None
        # RPC
        #self.rpcClient = zerorpc.Client()
        # update data
        self.update()
        
    def getWellNames(self):
      c = zerorpc.Client()
      c.connect("tcp://127.0.0.1:9138")
      return c.getWellNames()


    def update(self):
        if self.future is not None:
            # First make sure any pending tasks are cancelled.
            self.future.cancel()
            self.future = None

        self.future = self.executor.submit(partial(self.getData, self.wellName))
        # Setup the FutureWatcher to notify us of completion
        self.watcher = FutureWatcher(self.future)
        # by using FutureWatcher we ensure `dataReceived` slot will be
        # called from the main GUI thread by the Qt's event loop
        self.watcher.done.connect(self.dataReceived)
       

    def wellNameChanged(self):
      self.update()

    def getDomainWithUserDefinedColumns(self, userCols):
      columns = self.predefinedColumns + list(map(lambda col: ContinuousVariable.make(col), userCols))
      domain = Domain(columns, source = self.predefinedDomain)
      print("Domain: ", domain)
      return domain

    def getUserDefinedColumns(self, stage):
      columns = []
      for col in stage["userDefined"]:
        columns.append(col)
      return columns

    def getData(self, wellName):
      c = zerorpc.Client()
      c.connect("tcp://127.0.0.1:9138")
      data = c.getCompletion(wellName)
      completion = []
      domain = self.predefinedDomain
      if data:
        userCols = self.getUserDefinedColumns(data[0])
        domain = self.getDomainWithUserDefinedColumns(userCols)
        for stage in data:
          row = [stage["id"], 
                stage["mdStart"],
                stage["mdEnd"],
                stage["clustersNumber"],
                stage.get("totalProppant", math.nan),
                stage.get("totalFluid", math.nan)
          ]
          for column in userCols:
            row.append(stage["userDefined"].get(column, math.nan))
          completion.append(row)

      table = Orange.data.Table(domain)
      if completion:
        table = Orange.data.Table.from_numpy(domain, completion)
      
      print(table)
      return table
      
    @pyqtSlot(concurrent.futures.Future)
    def dataReceived(self, f):
      self.future = None
      try:
        results = f.result()
        self.table = results
        print(results)
        self.Outputs.data.send(self.table)
      except Exception as ex:
        self.error("Exception occurred during evaluation: {!r}".format(ex))

      

if __name__ == "__main__":
    WidgetPreview(CompletionInput).run()
