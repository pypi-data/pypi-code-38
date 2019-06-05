# These will be set at runtime if necessary
MACHINE_TYPES = None
MACHINE_TYPES_DEFAULT = None
FRAMEWORKS = None


def get_supported_options():
    """This is a stub, and gets filled in at runtime in spell/cli/main.py"""
    raise NotImplementedError()


# These are for lazily retrieving values at runtime
def get_machine_types():
    global MACHINE_TYPES, MACHINE_TYPES_DEFAULT
    if MACHINE_TYPES is None:
        MACHINE_TYPES, MACHINE_TYPES_DEFAULT = get_supported_options("machine_types")
    for t in MACHINE_TYPES:
        yield t


def get_machine_type_default():
    global MACHINE_TYPES, MACHINE_TYPES_DEFAULT
    if MACHINE_TYPES is None:
        MACHINE_TYPES, MACHINE_TYPES_DEFAULT = get_supported_options("machine_types")
    return MACHINE_TYPES_DEFAULT


def get_frameworks():
    global FRAMEWORKS, FRAMEWORKS_DEFAULT
    if FRAMEWORKS is None:
        FRAMEWORKS, FRAMEWORKS_DEFAULT = get_supported_options("frameworks")
    for f in FRAMEWORKS:
        yield f
