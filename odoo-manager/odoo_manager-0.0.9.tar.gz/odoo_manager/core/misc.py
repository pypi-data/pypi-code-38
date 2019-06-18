import os


def cleanup():
    """
    Cleans up everything related to the make process that runs for this specific
    module collection.

    :return {NoneType}:
    """
    os.system("rm -rf {}".format("_make_tmp"))
