from pylogcat import Level

class Log:
    level = Level.v

    @staticmethod
    def v(tag, msg):
        if Log.level <= Level.v:
            print('[V][{}] {}'.format(tag, msg))    
    @staticmethod    
    def i(tag, msg):
        if Log.level <= Level.i:
            print('[I][{}] {}'.format(tag, msg))
    @staticmethod    
    def w(tag, msg):
        if Log.level <= Level.w:
            print('[W][{}] {}'.format(tag, msg))
    @staticmethod 
    def e(tag, msg):
        if Log.level <= Level.e:
            print('[E][{}] {}'.format(tag, msg))