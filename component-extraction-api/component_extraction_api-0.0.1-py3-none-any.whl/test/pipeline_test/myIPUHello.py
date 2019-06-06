from runnable_pkg.modules.pipeline.AbstractPipelineUnit import AbstractPipelineUnit


class myIPUHello(AbstractPipelineUnit):

    def __init__(self):
        AbstractPipelineUnit.__init__(self)

    def execute(self, val):
        return {"Hello": ""}