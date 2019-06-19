from fastscore.suite import ModelManage as ModelManageBase

class ModelManage(ModelManageBase):

    def __init__(self, name):
        super(ModelManage, self).__init__(name)

    @classmethod
    def from_base(self, basemodelmanage):
        return ModelManage(basemodelmanage.name)
