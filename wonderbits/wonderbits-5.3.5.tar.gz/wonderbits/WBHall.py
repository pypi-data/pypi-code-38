from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

class Hall(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_magnetic(self, cb):
        self._register_event('hall{}'.format(self.index), 'magnetic', cb)
    
    def get_magnetic(self):
        """
        获取磁场强度值:rtype: float
        """

        command = 'hall{}.get_magnetic()'.format(self.index)
        return self._get_command(command)
    
    def calibrate(self, block = None):
        """
        校准霍尔传感器注意：校准过程中请确保没有磁性物体靠近模块，否则会导致校准后不准确。校准时，模块指示灯会变为黄色，等待指示灯变蓝说明校准完成了。

        :param block: 阻塞参数  False: 不阻塞 True: 阻塞
        """

        args = []
        if block != None:
            args.append(str(block))
        command = "hall{}.calibrate({})".format(self.index, ",".join(args))
        self._set_command(command)

    