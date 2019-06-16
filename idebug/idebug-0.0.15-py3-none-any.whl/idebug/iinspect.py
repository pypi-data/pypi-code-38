
import inspect


class DummyClass:

    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def dummy(self, var3=None):
        print(f"\n inspect.stack() :\n\n {inspect.stack()}")

def frame(frame):
    print(f"\n{'*'*60}\n Debug.frame")

    useful_frame_attrs = ['f_back','f_builtins','f_code','f_globals','f_locals']
    print_attrs(frame, 'frame', useful_frame_attrs)

    useful_frameinfo_attrs = ['filename','function']
    frameinfo = inspect.getframeinfo(frame)
    print_attrs(frameinfo, 'frameinfo', useful_frameinfo_attrs)

    useful_argvalues_attrs = ['args','count','index','keywords','locals','varargs']
    argvalues = inspect.getargvalues(frame)
    print_attrs(argvalues, 'argvalues', useful_argvalues_attrs)

def print_attrs(target, targetname, attrs):
    for attr in attrs:
        print(f"\n{'- '*30}\n {targetname}.{attr} :\n\n{target.__getattribute__(attr)}")
