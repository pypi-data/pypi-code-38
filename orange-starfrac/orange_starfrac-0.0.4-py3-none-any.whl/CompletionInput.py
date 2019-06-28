
import Orange.data
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.data import Domain, ContinuousVariable, StringVariable

import math

from orange_starfrac.RpcClient import RpcClient
from orange_starfrac.InputMixin import InputMixin


class CompletionInput(OWWidget, RpcClient, InputMixin):
    name = "Completion Data Input"
    description = "Retreive completion data from selected wells in the active tab of locally running StarFrac application"
    icon = "icons/input.svg"
    priority = 10
    predefinedColumns = [ "Stage", "MD start", "MD end", "# of clusters", "Total Proppant", "Total Fluid" ]
    domainVars = list(map(lambda col: ContinuousVariable.make(col), predefinedColumns))
    domainMetas = [StringVariable.make("Well")]
    predefinedDomain = Domain(domainVars, metas = domainMetas)

    want_main_area = False

    class Outputs:
        data = Output("Completion table", Orange.data.Table)


    def __init__(self):
        OWWidget.__init__(self)
        RpcClient.__init__(self)
        InputMixin.__init__(self)
        gui.button(self.controlArea, self, "Update", callback=self.update)
        self.update()

    def update(self):
        self.requestData("getCompletions", self.dataReceived)

    def dataReceived(self, data):
      wellNames = []
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
          row = self.fillUserDefinedRows(stage, userCols, row)
          completion.append(row)
          wellNames.append([stage["wellName"]])

      table = Orange.data.Table(domain)
      if completion:
        table = Orange.data.Table.from_numpy(domain, completion, metas=wellNames)
      print(table)
      self.table = table
      self.Outputs.data.send(self.table)


if __name__ == "__main__":
    WidgetPreview(CompletionInput).run()
