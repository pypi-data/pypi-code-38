
from Orange.data import Domain, ContinuousVariable
import math

class InputMixin():

    def getDomainWithUserDefinedColumns(self, userCols):
      columns = self.predefinedColumns + list(map(lambda col: ContinuousVariable.make(col), userCols))
      domain = Domain(columns, source = self.predefinedDomain, metas = self.domainMetas)
      return domain

    def getUserDefinedColumns(self, stage):
      columns = []
      if stage.get("userDefined", False):
        for col in stage["userDefined"]:
          columns.append(col)
      return columns


    def fillUserDefinedRows(self, stage, userCols, row):
      for column in userCols:
        value = math.nan
        try:
          value = float(stage["userDefined"].get(column, math.nan))
        except:
          pass
        row.append(value)
      return row


