from . import (AError, AOS)


class CommandLineTool_Error(AError.Error):
    pass


class CommandLineTool:
    def __init__(self, command, execFunc=AOS.system, execOutputFunc=AOS.systemOutput):
        self._command = command
        self._execFunc = execFunc  # 可通过functools.partial包装cmd以外的参数
        self._execOutputFunc = execOutputFunc  # 可通过functools.partial包装cmd以外的参数
        self._hasCheckExistence = False

    def checkExistence(self):
        if self._hasCheckExistence:
            return
        self._checkExistence()
        self._hasCheckExistence = True

    def _checkExistence(self):
        try:
            AOS.system('%s --version' % self._command, echo=False, nullout=True)
        except:
            raise CommandLineTool_Error('%s 命令行工具尚未安装' % self._command)

    @property
    def command(self):
        return self._command

    def setExecFunc(self, execFunc):
        self._execFunc = execFunc

    def setExecOutputFunc(self, execOutputFunc):
        self._execOutputFunc = execOutputFunc

    def execCommand(self, args):
        """执行命令"""
        self._execFunc('%s %s' % (self._command, args))

    def execOutputCommand(self, args):
        """执行命令并输出结果"""
        return self._execOutputFunc('%s %s' % (self._command, args))
