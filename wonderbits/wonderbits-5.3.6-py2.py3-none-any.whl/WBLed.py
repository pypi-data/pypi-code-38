from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

class Led(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def set_rgb(self, r, g, b):
        """
        设置彩灯颜色（r,g,b参数都设置为0时，关闭LED）

        :param r: 红色：0~255
        :param g: 绿色：0~255
        :param b: 蓝色：0~255
        """

        
        args = []    
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        command = 'led{}.set_rgb({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def fade_to_rgb(self, r, g, b, time, block = None, step = None):
        """
        控制彩灯由当前颜色在指定时间渐变到目标颜色

        :param r: 目标红色：0~255
        :param g: 目标绿色：0~255
        :param b: 目标蓝色：0~255
        :param time: 渐变时间：0~60 s  变化到目标颜色所用的时间
        :param block: 阻塞参数：  False: 不阻塞 True: 阻塞
        :param step: 变化次数：  在渐变时间内经过多少次变化达到目标颜色
        """

        
        args = []    
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        args.append(str(time))
        if block != None:
            args.append(str(block))
        if step != None:
            args.append(str(step))
        command = 'led{}.fade_to_rgb({})'.format(self.index, ",".join(args))
        self._set_command(command)

    