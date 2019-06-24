
from rook.processor.namespaces.python_object_namespace import PythonObjectNamespace
from rook.processor.namespaces.container_namespace import ContainerNamespace


class LogRecordNamespace(PythonObjectNamespace):

    def __init__(self, record):
        super(LogRecordNamespace, self).__init__(record, methods=self.METHODS)

    def format(self, args=None):
        return PythonObjectNamespace(self.obj.getMessage())

    def dump(self, args=None):
        return ContainerNamespace({
            'name': PythonObjectNamespace(self.obj.name),
            'msg': PythonObjectNamespace(self.obj.msg),
            'formatted_message': self.format(),
            'args': PythonObjectNamespace(self.obj.args),
            'level_name': PythonObjectNamespace(self.obj.levelname),
            'level_no': PythonObjectNamespace(self.obj.levelno),
            'path_name': PythonObjectNamespace(self.obj.pathname),
            'filename': PythonObjectNamespace(self.obj.filename),
            'module': PythonObjectNamespace(self.obj.module),
            'lineno': PythonObjectNamespace(self.obj.lineno),
            'function': PythonObjectNamespace(self.obj.funcName),
            'time': PythonObjectNamespace(self.obj.created),
            'thread_id': PythonObjectNamespace(self.obj.thread),
            'thread_name': PythonObjectNamespace(self.obj.threadName),
            'process_name': PythonObjectNamespace(self.obj.processName),
            'process_id': PythonObjectNamespace(self.obj.process)
        })

    METHODS = (format, dump)
