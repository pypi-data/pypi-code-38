from .wbits import Wonderbits





class Control(Wonderbits):
    def __init__(self, index=1):
        Wonderbits.__init__(self)
        self.index = index
        self.event = Control._Event(self)

    class _Event():
        def __init__(self, this):
            self.this = this

        def sw1_pressed(self):
            def wrapper(cb):
                self.this._register_event(
                    'control{}'.format(self.this.index), 'sw1', cb)
            return wrapper

        def sw2_pressed(self):
            def wrapper(cb):
                self.this._register_event(
                    'control{}'.format(self.this.index), 'sw2', cb)
            return wrapper

    
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
        该函数用于判断SW1是否被按下:rtype: bool
        """

        command = 'control{}.is_sw1_pressed()'.format(self.index)
        return self._get_command(command)
    
    def is_sw2_pressed(self):
        """
        该函数用于判断SW2是否被按下:rtype: bool
        """

        command = 'control{}.is_sw2_pressed()'.format(self.index)
        return self._get_command(command)
    
    def is_sw3_at_1(self):
        """
        该函数用于判断SW3的是否在1这侧:rtype: bool
        """

        command = 'control{}.is_sw3_at_1()'.format(self.index)
        return self._get_command(command)
    
    def get_sw4(self):
        """
        该函数用于判断获取SW4的位置:rtype: int
        """

        command = 'control{}.get_sw4()'.format(self.index)
        return self._get_command(command)
    
    def is_m1_connected(self):
        """
        该函数用于判断获取M1与COM是否导通，导通的判断是根据M1与COM之间的电阻率是否低于阈值，低于阈值判断为导通，高于阈值判断为不导通:rtype: bool
        """

        command = 'control{}.is_m1_connected()'.format(self.index)
        return self._get_command(command)
    
    def is_m2_connected(self):
        """
        该函数用于判断获取M2与COM是否导通，导通的判断是根据M2与COM之间的电阻率是否低于阈值，低于阈值判断为导通，高于阈值判断为不导通:rtype: bool
        """

        command = 'control{}.is_m2_connected()'.format(self.index)
        return self._get_command(command)
    
    def set_m1_m2_sensitivity(self, limit):
        """
        设置触摸灵敏度通过设置灵敏度改变M1，M2的触发阈值当get_m1_value或get_m2_value小于阈值时则认为M1或M2与COM导通

        :param limit: 灵敏度：0~100
        """

        args = []
        args.append(str(limit))
        command = "control{}.set_m1_m2_sensitivity({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def get_m1_value(self):
        """
        该函数用于获取M1的电阻率:rtype: float
        """

        command = 'control{}.get_m1_value()'.format(self.index)
        return self._get_command(command)
    
    def get_m2_value(self):
        """
        该函数用于获取M2的电阻率:rtype: float
        """

        command = 'control{}.get_m2_value()'.format(self.index)
        return self._get_command(command)
    