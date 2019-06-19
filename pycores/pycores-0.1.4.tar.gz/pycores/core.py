# Insert your code here. 

'''
Usage

@static_vars(counter = 0)
def foo():
    foo.counter += 1
'''
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate