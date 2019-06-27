import time, sys
__all__ = ['pprint', 'test']
class pprint():
    def __init__(self, *values, sep=' ', end='\n', flush=True):
        """print class"""
        self.message = str(sep).join(values)
        self.sep = sep
        self.end = end
        self.flush = flush
    def typing(self, speed=0.3):
        """how lower the speed how faster"""
        for i in list(self.message):
            print(i, end='', sep='')
            time.sleep(speed)
        print('', end=self.end)
        return
    def typ_stamp(self, speed=0.3):
        """how lower the speed how faster"""
        stamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        msg = stamp + str(self.message)
        for i in list(msg):
            print(i, end='', sep='')
            time.sleep(speed)
        print('', end=self.end)
        return
    def typ_red(self, speed=0.3):
        """how lower the speed how faster"""
        for i in list(self.message):
            print(i, file=sys.stderr, end='', sep='')
            time.sleep(speed)
        print('', end=self.end)
        return
    def red(self):
        print(self.message, sep=self.sep, end=self.end, flush=self.flush, file=sys.stderr)
    def timestamp(self):
        stamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        print(stamp, end=' ')
        print(self.message, sep=self.sep, end=self.end, flush=self.flush, file=sys.stdout)
        return
    def re_init(self, *values, sep=' ', end='\n', flush=True):
        """keep flush on else some things don't work"""
        self.message = str(sep).join(values)
        self.sep = sep
        self.end = end
        self.flush = flush
        return pprint(*values, sep=sep, end=end, flush=flush)
#test
def test():
    """test"""
    printer = pprint('test', 'hello')
    printer.typing(0.2)
    printer.red()
    printer.timestamp()
    pp = printer.re_init('test', 'hello', 're init')
    printer.typing()
    printer.red()
    printer.timestamp()
    pp.typing()
    pp.red()
    pp.timestamp()
    pp.re_init('test', 'hello', 're init', 'return')
    pp.typing(0.1)
    pp.red()
    pp.timestamp()
    pp.typ_stamp(0.1)
    pp.typ_red()
#if this is the main program:
if __name__ == '__main__':
    #then run test
    test()
