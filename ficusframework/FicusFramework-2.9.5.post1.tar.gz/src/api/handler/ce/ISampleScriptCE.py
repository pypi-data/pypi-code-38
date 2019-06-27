import warnings
from abc import abstractmethod

from api.handler.ce.ISimpleScriptCE import ISimpleScriptCE
from api.model.FdInputPipe import FdInputPipe

warnings.warn("'ISampleScriptCE'类已被废弃,请使用'ISimpleScriptCE'类代替 ", DeprecationWarning, 2)
class ISampleScriptCE(ISimpleScriptCE):
    """
    Python脚本式的CE的基类
    """

    @abstractmethod
    def do_compute(self,source_fds:FdInputPipe, params:dict):
        """
        计算器的业务逻辑
        :param source_fds: 输入源FD
        :param params: 计算器上下文参数
        :return: 返回一个 OutputWrapper的 数组
        """
        warnings.warn("'ISampleScriptCE'类已被废弃,请使用'ISimpleScriptCE'类代替 ", DeprecationWarning, 2)
        pass