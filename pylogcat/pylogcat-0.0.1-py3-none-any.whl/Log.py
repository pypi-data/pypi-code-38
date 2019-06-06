from pylogcat import Level

class Log:
    level = Level.v

    @staticmethod
    def v(tag, msg):
        if Log.level.value <= Level.v.value:
            print('[V][{}] {}'.format(tag, msg))    
    @staticmethod    
    def i(tag, msg):
        if Log.level.value <= Level.i.value:
            print('[I][{}] {}'.format(tag, msg))
    @staticmethod    
    def w(tag, msg):
        if Log.level.value <= Level.w.value:
            print('[W][{}] {}'.format(tag, msg))
    @staticmethod 
    def e(tag, msg):
        if Log.level.value <= Level.e.value:
            print('[E][{}] {}'.format(tag, msg))