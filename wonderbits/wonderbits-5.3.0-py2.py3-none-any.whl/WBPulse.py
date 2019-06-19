from .wbits import Wonderbits





class Pulse(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_heart_rate(self, cb):
        self._register_event('pulse{}'.format(self.index), 'heart_rate', cb)
    
    def register_heart_wave_received(self, cb):
        self._register_event('pulse{}'.format(self.index), 'heart_wave_received', cb)
    
    def get_heart_rate(self):
        """
        该函数用于获取模块检测的脉搏，此处的脉搏值表示一分钟脉搏跳动的次数测量时要求找到模块有汉字的一面，然后将手指轻轻的贴在此面，需要耐心等待一会则会测量出脉搏:rtype: int
        """

        command = 'pulse{}.get_heart_rate()'.format(self.index)
        return self._get_command(command)
    
    def get_unread_wave_count(self):
        """
        该函数用于获取脉搏波形队列中未读内容的个数，最多存储10个未读内容:rtype: int
        """

        command = 'pulse{}.get_unread_wave_count()'.format(self.index)
        return self._get_command(command)
    
    def get_heart_wave(self):
        """
        该函数用于获取脉搏波形队列中的未读波形值，读取后会删除这个数据如果没有未读的数据返回上一次的返回值:rtype: int
        """

        command = 'pulse{}.get_heart_wave()'.format(self.index)
        return self._get_command(command)
    