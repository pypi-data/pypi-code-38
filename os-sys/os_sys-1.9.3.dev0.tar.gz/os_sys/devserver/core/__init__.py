def core_setup():
    pass
class dict_list():
    def __init__(self, table={}):
        self.table = table
    def add(self, key, *data):
        self.table[key] = list(data)
    def get(self, key):
        return self.table[key]
    def get_table(self):
        return self.table
    def change(self, key, *data):
        data = list(data)
        old = self.table[key]
        item = data
        try:
            old = old + item
        except:
            pass
        new = old
        self.table[key] = new
        


class test():
    def __init__(self):
        print('test')
        self.data = 'test_'
class test1(test):
    def __init__(self):
        self.data = None
        print('test1')
        print(self.data)
        super().__init__()
        print(self.data)
        print('done!')
        self.__get__()
    def __get__(self):
        return 'test'
import threading
import psutil
def exec_return(code):
    import sys
    from io import StringIO
    import contextlib

    class Proxy(object):
        def __init__(self,stdout,stringio):
            self._stdout = stdout
            self._stringio = stringio
        def __getattr__(self,name):
            if name in ('_stdout','_stringio','write'):
                object.__getattribute__(self,name)
            else:
                return getattr(self._stringio,name)
        def write(self,data):
             self._stdout.write(data)
             self._stringio.write(data)

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = Proxy(sys.stdout,stdout)
        yield sys.stdout
        sys.stdout = old


    with stdoutIO() as s:
        exec(code)
    return s.getvalue()


class data(threading.Thread):
    def __init__(self):
        super().__init__()
    def run(self):
        #!/usr/bin/env python
        import psutil
        import time
        import datetime
        import time
        from tkinter import Tk, Canvas
        root = Tk()
        c = Canvas(root, width=2000, height=2000)
        while True:
            data = ''

            
            va = [
            psutil.disk_usage('C:\\'),
            dict(psutil.sensors_battery()._asdict()),
            dict(psutil.cpu_stats()._asdict()),
            psutil.virtual_memory() ,
            dict(psutil.virtual_memory()._asdict()),
            psutil.net_if_stats(),
            psutil.swap_memory(),
            str('cpu: '+str(psutil.cpu_percent())),
            psutil.cpu_times(),
            str('cpu count: ' + str(psutil.cpu_count())),
            psutil.cpu_times_percent(),
            
                 ]


            size = 800
            ypos = 10
            c.pack()
             
            
            c.create_text(625, ypos, text='-----------------------------------------------------------------------------------------------------------------------------------')
            import datetime
             
            now = datetime.datetime.now()
            for part in va:
                if '' in str(part):
                    part = str(part).replace("),", ',\n')
                ypos = ypos + 55
                c.create_text(625,ypos, fill='red',  font='Arail 12', text=''.join(str(part)))

            
            ypos = ypos + 65

            c.create_text(625, ypos, text='-----------------------------------------------------------------------------------------------------------------------------------------')
            root.update()
            time.sleep(0.1)
            c.delete("all")
def stats():
    data().start()
if __name__ == '__main__':
    stats()
