import clr

MASTA_PROPERTIES = dict()


def masta_property(func):
    ''' Decorator method for creating MASTA properties in Python

    Keyword arguments:
    -- func: The function that the decorator is wrapping
    '''
    global MASTA_PROPERTIES
    MASTA_PROPERTIES[func.__name__] = func
    return func


def init(path_to_dll_folder):
    '''Initialises the Python to MASTA API interop

    Keyword arguments:
    -- path_to_dll_folder: Path to your MASTA folder that
                           includes the MastaAPI.dll file
    '''
    clr.AddReference(path_to_dll_folder + "MastaAPI.dll")
    from SMT.MastaAPI import UtilityMethods
    UtilityMethods.InitialiseApiAccess(path_to_dll_folder)
