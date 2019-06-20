from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

class Buggy(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_battery_value(self, cb):
        self._register_event('buggy{}'.format(self.index), 'battery_value', cb)
    
    def register_s1(self, cb):
        self._register_event('buggy{}'.format(self.index), 's1', cb)
    
    def register_s2(self, cb):
        self._register_event('buggy{}'.format(self.index), 's2', cb)
    
    def register_tracer_state(self, cb):
        self._register_event('buggy{}'.format(self.index), 'tracer_state', cb)
    
    def get_battery_value(self):
        """
        获取电池电量值:rtype: int
        """

        command = 'buggy{}.get_battery_value()'.format(self.index)
        return self._get_command(command)
    
    def set_buzzer(self, frequency):
        """
        设置蜂鸣器声音频率（Hz）设置频率为0表示关闭蜂鸣器

        :param frequency: 频率：0~20000 Hz
        """

        args = []
        args.append(str(frequency))
        command = "buggy{}.set_buzzer({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_led1(self, r, g, b):
        """
        设置led1灯颜色（r,g,b参数都设置为0时，关闭LED）

        :param r: 红色：0~255
        :param g: 绿色：0~255
        :param b: 蓝色：0~255
        """

        args = []
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        command = "buggy{}.set_led1({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_led2(self, r, g, b):
        """
        设置led1灯颜色（r,g,b参数都设置为0时，关闭LED）

        :param r: 红色：0~255
        :param g: 绿色：0~255
        :param b: 蓝色：0~255
        """

        args = []
        args.append(str(r))
        args.append(str(g))
        args.append(str(b))
        command = "buggy{}.set_led2({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_motor(self, speed_left, speed_right):
        """
        设置电机A转动

        :param speed_left: 转速：-100~100  符号表示转动方向，绝对值为转动速度
        :param speed_right: 转速：-100~100  符号表示转动方向，绝对值为转动速度
        """

        args = []
        args.append(str(speed_left))
        args.append(str(speed_right))
        command = "buggy{}.set_motor({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def get_s1(self):
        """
        获取s1检测的亮度值亮度值代表相对强度，值越大代表亮度越强:rtype: float
        """

        command = 'buggy{}.get_s1()'.format(self.index)
        return self._get_command(command)
    
    def get_s2(self):
        """
        获取s2检测的亮度值亮度值代表相对强度，值越大代表亮度越强:rtype: float
        """

        command = 'buggy{}.get_s2()'.format(self.index)
        return self._get_command(command)
    
    def get_tracer_all_black_state(self):
        """
        判断循迹传感器是否全部检测为黑:rtype: bool
        """

        command = 'buggy{}.get_tracer_all_black_state()'.format(self.index)
        return self._get_command(command)
    
    def get_tracer_all_white_state(self):
        """
        判断循迹传感器是否全部检测为白:rtype: bool
        """

        command = 'buggy{}.get_tracer_all_white_state()'.format(self.index)
        return self._get_command(command)
    
    def get_tracer_state(self, channel):
        """
        判断某个循迹传感器是否检测为黑:rtype: bool
        """

        command = 'buggy{}.get_tracer_state()'.format(self.index)
        return self._get_command(command)
    
    def get_tracer_value(self, channel):
        """
        获取某个循迹传感器的检测值:rtype: float
        """

        command = 'buggy{}.get_tracer_value()'.format(self.index)
        return self._get_command(command)
    
    def get_t6(self):
        """
        判断t6是否无遮挡:rtype: bool
        """

        command = 'buggy{}.get_t6()'.format(self.index)
        return self._get_command(command)
    
    def get_t7(self):
        """
        判断t7是否无遮挡:rtype: bool
        """

        command = 'buggy{}.get_t7()'.format(self.index)
        return self._get_command(command)
    
    def set_calibration_percentage(self, value):
        """
        设置循迹传感器的阈值百分比为value阈值=循迹传感器检测的黑色值*value%+循迹传感器检测的白色值*（1-value%）

        :param value: 值：0~100
        """

        args = []
        args.append(str(value))
        command = "buggy{}.set_calibration_percentage({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def calibration_black(self):
        """
        校准循迹传感器的黑色值

        """

        args = []
        command = "buggy{}.calibration_black({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def calibration_white(self):
        """
        校准循迹传感器的白色值

        """

        args = []
        command = "buggy{}.calibration_white({})".format(self.index, ",".join(args))
        self._set_command(command)

    