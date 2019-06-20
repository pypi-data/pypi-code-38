from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

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
        获取温度值（°C）:rtype: int
        """

        command = 'observer{}.get_temperature()'.format(self.index)
        return self._get_command(command)
    
    def get_humidity(self):
        """
        获取湿度值(%RH）:rtype: int
        """

        command = 'observer{}.get_humidity()'.format(self.index)
        return self._get_command(command)
    
    def get_light(self):
        """
        获取亮度值亮度值代表相对强度，值越大代表亮度越强:rtype: int
        """

        command = 'observer{}.get_light()'.format(self.index)
        return self._get_command(command)
    
    def get_volume(self):
        """
        获取声音强度值声音强度值代表相对强度，值越大代表声音越响:rtype: int
        """

        command = 'observer{}.get_volume()'.format(self.index)
        return self._get_command(command)
    