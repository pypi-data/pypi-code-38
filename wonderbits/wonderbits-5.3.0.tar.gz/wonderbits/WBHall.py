from .wbits import Wonderbits





class Hall(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_magnetic(self, cb):
        self._register_event('hall{}'.format(self.index), 'magnetic', cb)
    
    def get_magnetic(self):
        """
        该函数用于获取霍尔检测的磁场强度值:rtype: float
        """

        command = 'hall{}.get_magnetic()'.format(self.index)
        return self._get_command(command)
    
    def calibrate(self, block = None):
        """
        校准霍尔传感器零点使用该函数时，霍尔模块指示灯会在校准执行过程中变为黄色，校准完成后回复原有颜色。校准过程中保证没有磁性物体靠近模块，否则会导致校准后的零点不准确。

        :param block: 阻塞参数：  False表示不阻塞 True表示阻塞
        """

        args = []
        if block != None:
            args.append(str(block))
        command = "hall{}.calibrate({})".format(self.index, ",".join(args))
        self._set_command(command)

    