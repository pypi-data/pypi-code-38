"""
    Common functions used by Click and Invoke
"""
import os
import logging
import importlib
from tornado.options import options
from contextlib import contextmanager


@contextmanager
def pid_file(path):
    """ creates a file with the process id and removes it """
    pid = os.getpid()
    with open(path, "w") as f:
        f.write(f"{pid}")
    yield
    if os.path.isfile(path):
        os.unlink(path)


def import_module(name):
    "Íts ok not to have the module but not ok to not have dependants."
    try:
        logging.info("looking for module %s", name)
        return importlib.import_module(name)
    except ModuleNotFoundError as ex:
        if name not in str(ex):
            raise


def get_module(name):
    if name is None:
        print("module expected")
    else:
        md = importlib.import_module(name)
        procs = importlib.import_module(f"{name}.procedures")
        if procs:
            if not getattr(procs, "__all__"):
                print(f"expected __all__ in procedures module")
            else:
                options["procedures"] = f"{name}.procedures"
                ext_log = import_module(f"{name}.log")
                if ext_log:
                    options["log_extend"] = f"{name}.log:extend"
                ext_settings = import_module(f"{name}.settings")
                if ext_settings:
                    options["settings_extend"] = f"{name}.settings:extend"
                ext_urls = import_module(f"{name}.urls")
                if ext_urls:
                    options["urls_extend"] = f"{name}.urls:extend"
                return True
        else:
            print(f"expected procedures in {name}")
