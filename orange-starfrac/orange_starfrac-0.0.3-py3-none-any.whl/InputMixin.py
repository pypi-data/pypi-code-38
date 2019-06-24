
from Orange.data import Domain, ContinuousVariable

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


