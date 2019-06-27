import cProfile
import pstats
from _io import StringIO
import inspect
import collections


def log_calls(function):
    '''
    Decorator that logs function calls in their self.log
    '''
    def wrapper(self,*args,**kwargs):  
        self.log.log(group=function.__name__,message='Enter') 
        function(self,*args,**kwargs)
        self.log.log(group=function.__name__,message='Exit') 
    return wrapper

def add_runtime(function):
    '''
    Decorator that adds a runtime profile object to the output
    '''
    def wrapper(*args,**kwargs):  
        pr=cProfile.Profile()
        pr.enable()
        output = function(*args,**kwargs)
        pr.disable()
        return pr,output
    return wrapper

def print_memory(function):
    '''
    Decorator that prints memory information at each call of the function
    '''
    import memory_profiler
    def wrapper(*args,**kwargs):
        m = StringIO()
        temp_func = memory_profiler.profile(func = function,stream=m,precision=4)
        output = temp_func(*args,**kwargs)
        print(m.getvalue())
        m.close()
        return output
    return wrapper
    
def print_profile(function):
    '''
    Decorator that prints memory and runtime information at each call of the function
    '''
    import memory_profiler
    def wrapper(*args,**kwargs):
        m=StringIO()
        pr=cProfile.Profile()
        pr.enable()
        temp_func = memory_profiler.profile(func=function,stream=m,precision=4)
        output = temp_func(*args,**kwargs)
        print(m.getvalue())
        pr.disable()
        ps = pstats.Stats(pr)
        ps.sort_stats('cumulative').print_stats('(?!.*memory_profiler.*)(^.*$)',20)
        m.close()
        return output
    return wrapper

def empty_function():
        pass
def doc_string_only_function():
        '''
        '''
        pass
    
def _strip_function(function):
    if isinstance(function,staticmethod):
        function=function.__get__(object)#Access to implementation of staticmethod
    elif not hasattr(function,'__name__') or '.' in function.__qualname__:
        raise ValueError('Can only declare top-level functions and static methods as actions'.format(function))
    name = function.__qualname__
    return (function,name)

def find_implementation(cl,declaration):
    for a in cl.__dict__.values():
        if isinstance(a,implementation) and (declaration in a.targets or not a.targets):
            return a.function

class default(object):
    '''
    Declare abstract function and provide default implementation that will be overwritten 
    if first argument redefines what semantics does to it.
    '''
    def __init__(self,function,name=None):
        self.function,name2=_strip_function(function)
        self.name=name or name2
        self.implementations=collections.OrderedDict()
        self.memory_size=10

    def __call__(self,*args,**kwargs):
        if not args:
            raise ValueError('Must specify at least one argument to act on')
        if isinstance(args[0],object):
            cl=args[0].__class__
            if not cl in self.implementations:
                self.implementations[cl]=find_implementation(cl,declaration) or self.function
                if len(self.implementations)>self.memory_size:
                    self.implementations.popitem(last=False)
            return self.implementations[cl](*args,**kwargs)
        else:
            return self.function(*args,**kwargs)

def declaration(function):
    '''
    Declare abstract function. 
    
    Requires function to be empty except for docstring describing semantics.
    To apply function, first argument must come with implementation of semantics.
    '''
    function,name=_strip_function(function)
    if not function.__code__.co_code in [empty_function.__code__.co_code, doc_string_only_function.__code__.co_code]: 
        raise ValueError('Declaration requires empty function definition')
    def not_implemented_function(*args,**kwargs):
        raise ValueError('Argument \'{}\' did not specify how \'{}\' should act on it'.format(args[0],name))
    not_implemented_function.__qualname__=not_implemented_function.__name__ 
    return default(not_implemented_function,name=name)

class implementation(object):
    '''
    Implement declaration
    '''
    def __init__(self, *targets):
        self.initialized=False
        if all(isinstance(target,default) for target in targets):
            self.targets=targets
        else:
            raise ValueError('Target is not a declaration (Did you forget to pass a declaration within parentheses to `implementation`?)')

    def __call__(self,*args,**kwargs):#Allow all possible argument combinations to make sure correct error message is displayed when tried to use directly
        if not self.initialized and len(args)==1 and not kwargs:
            function=args[0]
            if inspect.isfunction(function):
                self.initialized=True
                self.function=function
                return self
            else:
                raise ValueError('Only methods can implement declarations')
        else:
            raise ValueError('Cannot call implementation with method syntax. Use `{1}` instead. To access underlying function, use `function` attribute of \'{0}\''.format(
                self.function.__name__,
                '` or `'.join([target.name+'(...)' for target in self.targets]))) 
            
class memoize(object):
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
    def __call__(self, *args,**kwargs):
        try:
            if (args,kwargs) in self.memo:
                pass
            if args not in self.memo:
                self.memo[args] = self.fn(*args)
            return self.memo[args]
        except:
            return self.fn(*args,**kwargs)


def print_runtime(function):
    '''
    Decorator that prints running time information at each call of the function
    '''
    def wrapper(*args,**kwargs):
        pr=cProfile.Profile()
        pr.enable()
        output = function(*args,**kwargs)
        pr.disable()
        ps = pstats.Stats(pr)
        ps.sort_stats('tot').print_stats(20)
        return output
    return wrapper

def print_peak_memory(func,stream = None):
    """
    Print peak memory usage (in MB) of a function call
    
    :param func: Function to be called
    :param stream: Stream to write peak memory usage (defaults to stdout)  
    
    https://stackoverflow.com/questions/9850995/tracking-maximum-memory-usage-by-a-python-function
    """
    import time
    import psutil
    import os
    memory_denominator=1024**2
    memory_usage_refresh=0.05
    def wrapper(*args,**kwargs):
        from multiprocessing.pool import ThreadPool
        pool = ThreadPool(processes=1)
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        delta_mem = 0
        max_memory = 0
        async_result = pool.apply_async(func, args,kwargs)
        # do some other stuff in the main process
        while(not async_result.ready()):
            current_mem = process.memory_info().rss
            delta_mem = current_mem - start_mem
            if delta_mem > max_memory:
                max_memory = delta_mem
            # Check to see if the library call is complete
            time.sleep(memory_usage_refresh)
        
        return_val = async_result.get()  # get the return value from your function.
        max_memory /= memory_denominator
        if stream is not None:
            stream.write(str(max_memory))
        return return_val
    return wrapper

if __name__=='__main__':
    import numpy as np
    @print_peak_memory
    def f(x):
        return np.mean(np.random.rand(1000000000))
    print(f(3))


    @declaration
    def read_out(a,loudness='loudly',c=1):
        pass
        #print('I say',a,'loudly')
        
    class reading(object):
        @staticmethod
        def ee(self,loudness='loudly'):
            pass
        @default
        @staticmethod
        def read_out(self,loudness='loudly',c=1):
            pass
    class Test(object):
        def test(self):
            pass
        @staticmethod
        def te(self):
            print(self)
    class French2(object):
        @implementation(reading.read_out,read_out)
        def gar(self,loudness='tres fort'):
            pass
            #print('Je dit deux',loudness)
        @implementation(read_out) 
        def read_out(self,*args):
            #print('noo')
            pass
        
    
