#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-02-24 21:23


def debugdeco(func):
    def wapper(*args, **kwargs):
        print("[DEBUG]:enter {}()".format(func.__name__))
        return func(*args, **kwargs)
    return wapper


@ debugdeco
def say(something):
    print("hello {}".format(something))












