from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

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
        获取脉搏（每分钟脉搏跳动次数）测量时，从正面（有字的那面）将手指轻轻的贴在绿灯上，等待10秒左右方可测得准确的脉搏值:rtype: int
        """

        command = 'pulse{}.get_heart_rate()'.format(self.index)
        return self._get_command(command)

    
    def get_unread_wave_count(self):
        """
        获取脉搏波形队列中未读内容的个数（最多存储10个未读内容）返回为0时，说明没有未读取的内容:rtype: int
        """

        command = 'pulse{}.get_unread_wave_count()'.format(self.index)
        return self._get_command(command)

    
    def get_heart_wave(self):
        """
        获取脉搏波形强度值如果没有未读的数据,则返回上一次的值:rtype: int
        """

        command = 'pulse{}.get_heart_wave()'.format(self.index)
        return self._get_command(command)

    