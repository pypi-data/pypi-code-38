from .wbits import Wonderbits





class Driver(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def set_motor_a(self, speed, time = None, block = None):
        """
        设置电机A转动

        :param speed: 转速：-100~100  符号不同表示转动方向不同，绝对值为转动速度
        :param time: 变速时间，从当前转速转变到设置转速用到的时间，单位 ms  默认值为10
        :param block: 阻塞参数：  False表示不阻塞 True表示阻塞
        """

        args = []
        args.append(str(speed))
        if time != None:
            args.append(str(time))
        if block != None:
            args.append(str(block))
        command = "driver{}.set_motor_a({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def stop_motor_a(self):
        """
        设置电机A停止转动

        """

        args = []
        command = "driver{}.stop_motor_a({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_motor_b(self, speed, time = None, block = None):
        """
        设置电机B转动

        :param speed: 转速：-100~100  符号不同表示转动方向不同，绝对值为转动速度
        :param time: 变速时间，从当前转速转变到设置转速用到的时间，单位 ms  默认值为10
        :param block: 阻塞参数：  False表示不阻塞 True表示阻塞
        """

        args = []
        args.append(str(speed))
        if time != None:
            args.append(str(time))
        if block != None:
            args.append(str(block))
        command = "driver{}.set_motor_b({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def stop_motor_b(self):
        """
        设置电机B停止转动

        """

        args = []
        command = "driver{}.stop_motor_b({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_servo1(self, angle):
        """
        设置舵机1转动到指定角度使用此函数后舵机1将拥有维持角度的扭矩，施加外力改变舵机1的角度会很困难

        :param angle: 角度：0~180
        """

        args = []
        args.append(str(angle))
        command = "driver{}.set_servo1({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def stop_servo1(self):
        """
        关闭舵机1使用此函数后舵机1将失去维持角度的扭矩，施加外力可以轻松改变舵机1的角度

        """

        args = []
        command = "driver{}.stop_servo1({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_servo2(self, angle):
        """
        设置舵机2转动到指定角度使用此函数后舵机2将拥有维持角度的扭矩，施加外力改变舵机2的角度会很困难

        :param angle: 角度：0~180
        """

        args = []
        args.append(str(angle))
        command = "driver{}.set_servo2({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def stop_servo2(self):
        """
        关闭舵机2使用此函数后舵机2将失去维持角度的扭矩，施加外力可以轻松改变舵机2的角度

        """

        args = []
        command = "driver{}.stop_servo2({})".format(self.index, ",".join(args))
        self._set_command(command)

    