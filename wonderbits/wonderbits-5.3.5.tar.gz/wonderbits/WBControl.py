from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

class Control(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_sw1(self, cb):
        self._register_event('control{}'.format(self.index), 'sw1', cb)
    
    def register_sw2(self, cb):
        self._register_event('control{}'.format(self.index), 'sw2', cb)
    
    def register_sw3(self, cb):
        self._register_event('control{}'.format(self.index), 'sw3', cb)
    
    def register_sw4(self, cb):
        self._register_event('control{}'.format(self.index), 'sw4', cb)
    
    def register_m1(self, cb):
        self._register_event('control{}'.format(self.index), 'm1', cb)
    
    def register_m2(self, cb):
        self._register_event('control{}'.format(self.index), 'm2', cb)
    
    def register_m1_value(self, cb):
        self._register_event('control{}'.format(self.index), 'm1_value', cb)
    
    def register_m2_value(self, cb):
        self._register_event('control{}'.format(self.index), 'm2_value', cb)
    
    def is_sw1_pressed(self):
        """
        判断按键SW1是否被按下:rtype: bool
        """

        command = 'control{}.is_sw1_pressed()'.format(self.index)
        return self._get_command(command)
    
    def is_sw2_pressed(self):
        """
        判断按键SW2是否被按下:rtype: bool
        """

        command = 'control{}.is_sw2_pressed()'.format(self.index)
        return self._get_command(command)
    
    def is_sw3_at_1(self):
        """
        判断SW3的是否在‘1’的位置（‘1’指的是电路上白色的数字）:rtype: bool
        """

        command = 'control{}.is_sw3_at_1()'.format(self.index)
        return self._get_command(command)
    
    def get_sw4(self):
        """
        获取SW4的位置值:rtype: int
        """

        command = 'control{}.get_sw4()'.format(self.index)
        return self._get_command(command)
    
    def is_m1_connected(self):
        """
        判断获取M1与COM是否导通一般的使用方法是：将连接线插入到控制模块的接头上，实验者一手握住COM线头（黑色），另一手握住M1或M2线头（黄或绿色）。导通时板子上相应指示灯会亮起:rtype: bool
        """

        command = 'control{}.is_m1_connected()'.format(self.index)
        return self._get_command(command)
    
    def is_m2_connected(self):
        """
        判断获取M2与COM是否导通一般的使用方法是：将连接线插入到控制模块的接头上，实验者一手握住COM线头（黑色），另一手握住M1或M2线头（黄或绿色）。导通时板子上相应指示灯会亮起:rtype: bool
        """

        command = 'control{}.is_m2_connected()'.format(self.index)
        return self._get_command(command)
    
    def set_m1_m2_sensitivity(self, limit):
        """
        设置M1和M2灵敏度灵敏度越高，is_m1_connected()和is_m2_connected()越容易返回True

        :param limit: 灵敏度：0~100
        """

        args = []
        args.append(str(limit))
        command = "control{}.set_m1_m2_sensitivity({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def get_m1_value(self):
        """
        获取M1的电阻率:rtype: float
        """

        command = 'control{}.get_m1_value()'.format(self.index)
        return self._get_command(command)
    
    def get_m2_value(self):
        """
        获取M2的电阻率:rtype: float
        """

        command = 'control{}.get_m2_value()'.format(self.index)
        return self._get_command(command)
    