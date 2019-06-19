from .wbits import Wonderbits





class Led(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def set_rgb(self, r, g, b):
        """
        设置彩灯颜色三个参数都为0时，表示灯不发光

        :param r: 红色：0~255
        :param g: 绿色：0~255
        :param b: 蓝色：0~255
        """

        args = []
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        command = "led{}.set_rgb({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def fade_to_rgb(self, r, g, b, time, step = None, block = None):
        """
        设置彩灯由当前颜色渐变到目标颜色

        :param r: 目标红色：0~255
        :param g: 目标绿色：0~255
        :param b: 目标蓝色：0~255
        :param time: 渐变时间：0~60000ms  经过这个时间变化到目标颜色
        :param step: 变化次数：  在渐变时间内经过多少次变化达到目标颜色
        :param block: 阻塞参数：  False表示不阻塞 True表示阻塞
        """

        args = []
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        args.append(str(time))
        if step != None:
            args.append(str(step))
        if block != None:
            args.append(str(block))
        command = "led{}.fade_to_rgb({})".format(self.index, ",".join(args))
        self._set_command(command)

    