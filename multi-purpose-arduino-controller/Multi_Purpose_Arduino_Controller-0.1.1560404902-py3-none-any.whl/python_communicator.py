import logging

from filter_dict import filter_dict


class TargetNotFoundException(Exception):
    pass


class PythonCommunicator():
    def __init__(self,logger=None):
        self._registered_nodes = dict()
        self.logger = logger if logger is not None else logging.getLogger("PythonCommunicator")


    def get_node(self, name):
        return self._registered_nodes.get(name)

    def add_node(self, name, target):
        self._registered_nodes[name] = target

    def cmd_out(self, cmd, targets=None, **kwargs):
        if targets is None:
            targets=list(self._registered_nodes.keys())

        for target in targets:
            node = self.get_node(target)
            if node is not None:
                if isinstance(node, PythonCommunicator):
                    node.cmd_in(cmd, **kwargs)
                else:
                    try:
                        method_to_call = getattr(node, cmd)
                        method_to_call(**filter_dict(kwargs, method_to_call))
                    except Exception as e:
                        #self.logger.exception(e)
                        pass
            else:
                raise TargetNotFoundException("target: "+str(target)+" not found in nodes ("+','.join(self._registered_nodes)+")")

    def cmd_in(self, cmd, **kwargs):
        print(cmd, kwargs)

