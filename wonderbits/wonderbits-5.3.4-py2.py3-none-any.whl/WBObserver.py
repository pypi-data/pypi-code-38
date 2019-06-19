from .wbits import Wonderbits





class Observer(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_temperature(self, cb):
        self._register_event('observer{}'.format(self.index), 'temperature', cb)
    
    def register_humidity(self, cb):
        self._register_event('observer{}'.format(self.index), 'humidity', cb)
    
    def register_light(self, cb):
        self._register_event('observer{}'.format(self.index), 'light', cb)
    
    def register_volume(self, cb):
        self._register_event('observer{}'.format(self.index), 'volume', cb)
    
    def get_temperature(self):
        """
        该函数用于获取模块检测的温度值，单位°C:rtype: int
        """

        command = 'observer{}.get_temperature()'.format(self.index)
        return self._get_command(command)
    
    def get_humidity(self):
        """
        该函数用于获取模块检测的湿度值，这里测量的湿度为相对湿度单位%RH:rtype: int
        """

        command = 'observer{}.get_humidity()'.format(self.index)
        return self._get_command(command)
    
    def get_light(self):
        """
        该函数用于获取模块检测的亮度值，这里的亮度值代表一种量级无单位，值越大代表亮度越强。用手遮挡住传感器的无光环境监测值为0，使用手机闪光灯发光时对准检测亮度传感器值为100。:rtype: int
        """

        command = 'observer{}.get_light()'.format(self.index)
        return self._get_command(command)
    
    def get_volume(self):
        """
        该函数用于获取模块检测的声音强度值，这里的亮度值代表一种量级无单位，值越大代表声音强度越强。安静为0，声源需要靠近传感器效果会更好。:rtype: int
        """

        command = 'observer{}.get_volume()'.format(self.index)
        return self._get_command(command)
    