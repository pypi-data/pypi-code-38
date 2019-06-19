from .wbits import Wonderbits





class Ultrasonic(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_distance(self, cb):
        self._register_event('ultrasonic{}'.format(self.index), 'distance', cb)
    
    def get_distance(self):
        """
        该函数用于获取超声波检测的距离值，单位：cm:rtype: float
        """

        command = 'ultrasonic{}.get_distance()'.format(self.index)
        return self._get_command(command)
    