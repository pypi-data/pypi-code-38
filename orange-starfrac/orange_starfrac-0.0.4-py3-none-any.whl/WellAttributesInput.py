
import Orange.data
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.data import Domain, ContinuousVariable, StringVariable

import math

from orange_starfrac.RpcClient import RpcClient
from orange_starfrac.InputMixin import InputMixin


class WellAttributesInput(OWWidget, RpcClient, InputMixin):
    name = "Well Attributes Data Input"
    description = "Retreive Well Attributes from selected wells in the active tab of locally running StarFrac application"
    icon = "icons/input.svg"
    priority = 20
    predefinedColumns = [ "Total # of stages", "Total Proppant", "Total Fluid", "Completed Length",
                          "12 month production"]
    want_main_area = False

    domainVars = list(map(lambda col: ContinuousVariable.make(col), predefinedColumns))
    domainMetas = [StringVariable.make("Well")]
    predefinedDomain = Domain(domainVars, metas = domainMetas)


    class Outputs:
        data = Output("Well Attributes table", Orange.data.Table)

    def __init__(self):
        OWWidget.__init__(self)
        RpcClient.__init__(self)
        InputMixin.__init__(self)
        gui.button(self.controlArea, self, "Update", callback=self.update)
        self.update()

    def update(self):
        self.requestData("getWellAttributes", self.dataReceived)

    def dataReceived(self, data):
      metas = []
      tableData = []
      domain = self.predefinedDomain
      if data:
        userCols = self.getUserDefinedColumns(data[0])
        domain = self.getDomainWithUserDefinedColumns(userCols)
        for stage in data:
          row = [
                stage.get("totalStages", math.nan),
                stage.get("totalProppant", math.nan),
                stage.get("totalFluid", math.nan),
                stage.get("completedLength", math.nan),
                stage.get("production12", math.nan)
          ]
          row = self.fillUserDefinedRows(stage, userCols, row)
          tableData.append(row)
          metas.append([stage["well"]])

      table = Orange.data.Table(domain)
      if tableData:
        table = Orange.data.Table.from_numpy(domain, tableData, metas=metas)

      print(table)
      self.Outputs.data.send(table)



if __name__ == "__main__":
    WidgetPreview(WellAttributesInput).run()
