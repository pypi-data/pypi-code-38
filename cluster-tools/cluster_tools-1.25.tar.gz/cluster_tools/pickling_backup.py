import sys
import os
import io
if 'USE_CLOUDPICKLE' in os.environ:
    import cloudpickle
    pickle_strategy = cloudpickle
else:
    import pickle
    pickle_strategy = pickle
import importlib
from .util import warn_after

WARNING_TIMEOUT = 10 * 60 # seconds



class PickleDumpWrapper():

    def __init__(self, obj):
        print("init of pickle dump wrapper")
        self.obj = obj
        self.main_path = file_path_to_absolute_module(sys.argv[0])


        # main_module = importlib.import_module(main_path)
        # fun = getattr(main_module, fun.__name__)
    
    def __setstate__(self, state):
        print("__set state")
        self.obj = state["obj"]
        self.main_path = state["main_path"]
        PickleDumpWrapper.main_path = self.main_path


PickleDumpWrapper.main_path = None

@warn_after("pickle.dumps", WARNING_TIMEOUT)
def dumps(*args, **kwargs):
    obj = pickle_strategy.dumps(*args, **kwargs)
    main_path = file_path_to_absolute_module(sys.argv[0])
    return obj.replace(b'__main__', str.encode(main_path))
     
    obj = PickleDumpWrapper(args[0])
    # obj = args[0]

    return pickle_strategy.dumps(obj, *args[1:], **kwargs)


def file_path_to_absolute_module(file_path):
    """
    Given a file path, return an import path.
    :param file_path: A file path.
    :return:
    """
    assert os.path.exists(file_path)
    file_loc, ext = os.path.splitext(file_path)
    assert ext in ('.py', '.pyc')
    directory, module = os.path.split(file_loc)
    module_path = [module]
    while True:
        if os.path.exists(os.path.join(directory, '__init__.py')):
            directory, package = os.path.split(directory)
            module_path.append(package)
        else:
            break
    path = '.'.join(module_path[::-1])
    return path


class CustomUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        print("Finding class for", module, name)
        if name == PickleDumpWrapper.__name__:
            print("find_class finds pickle dump wrapper")
            return PickleDumpWrapper
        elif module == "__main__":
            print("Can we use this for __main__?", PickleDumpWrapper.main_path)
            main_path = "test.py"
            main_module = importlib.import_module(main_path)
            fun = getattr(main_module, name)
            return fun

        # if name == 'Manager':
        #     from settings import Manager
        #     return Manager
        return super().find_class(module, name)


@warn_after("pickle.loads", WARNING_TIMEOUT)
def loads(*args, **kwargs):
    return pickle_strategy.loads(*args, **kwargs)

    wrapper = CustomUnpickler(io.BytesIO(*args)).load()

    return wrapper.obj
