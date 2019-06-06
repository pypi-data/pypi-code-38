import inspect,sys

from . import coloring


def _get_default_kwargs(function):

    if sys.version_info[0]==2:
        # python 2
        a = inspect.getargspec(function)
    else :
        # python 3
        a = inspect.getfullargspec(function)
    args = a.args
    defaults = a.defaults
    args = args[-len(defaults):]
    r = {a:d for a,d in zip(args,defaults)}
    return r


def _ask_if_user_ok(kwargs):

    print("\n\tcompiling using arguments: ")
    for arg,value in kwargs.items():
        print("\t\t"+arg+": "
              +coloring.green(str(value)))

    answered = False
        
    while not answered :
        
        request = "\t\t\t\t\tok ? (Y|N) "

        try :
            # python 2
            value = raw_input(request)
        except :
            # python 3
            value = input(request)

        value = value.strip()
            
        if value in ["Y","y","N","n"]:
            answered = True

    if value in ["Y","y"]:
        print("\n\n")
        return True

    print("\n\n")
    return False


def _get_input(arg,default,max_attemps=5):

    def _ask_user(arg,default):

        request = str( "\t"+ str(arg)
                       + "( "+coloring.green( str(default)) +" ) : ")

        try :
            # python 2
            value = raw_input(request)
        except :
            # python 3
            value = input(request)

        try :
            value = eval(value)
        except :
            value = str(value)
            value = value.strip()
            
        if value == "":
            value = default
            
        return value

    done = False
    attemps = 0
    value = _ask_user(arg,default)
    return value
    


# functions is expected to be a list of
# tuples (function, args, kwargs)

def interactive_execute(functions):

    # all default kwargs for each function
    # set in one dict

    default_kwargs = {}

    for function,_,__ in functions:
        
        kwargs = _get_default_kwargs(function)
        for arg,value in kwargs.items():
            default_kwargs[arg]=value
        
    
    # overwriting default value by value
    # set in configuration.yaml
    
    for _,__,kwargs in functions :

        for arg,value in kwargs.items():
            default_kwargs[arg]=value


    # overwriting values by user input
            
    user_kwargs = {}

    for arg,default in default_kwargs.items() :
        value = _get_input(arg,default)
        user_kwargs[arg]=value

    # double checking with user all is fine:
    
    user_ok =  _ask_if_user_ok(user_kwargs)
        
    if not user_ok :
        return interactive_execute(functions)
        
    # calling all the functions with
    # collected args

    scripts = []
    
    for function,args,kwargs in functions:

        for arg,default in user_kwargs.items():
            if arg in kwargs.keys():
                kwargs[arg]=default

        script = function(*args,**kwargs)
        scripts.append(script)

    return "\n".join(script)
