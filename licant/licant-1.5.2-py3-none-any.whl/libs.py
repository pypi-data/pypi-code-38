from licant.scripter import scriptq
from licant.util import yellow
import licant.core

import os
import sys
import json

gpath = "/var/lib/licant"
lpath = os.path.expanduser("~/.licant")

libs = None

included = dict()


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def init():
    global libs

    glibs = {}
    llibs = {}

    if os.path.exists(gpath):
        glibs = json.load(open(gpath))

    if os.path.exists(lpath):
        llibs = json.load(open(lpath))

    libs = merge_two_dicts(glibs, llibs)


def include(lib, path=None, local_tunel=None):
    if libs is None:
        init()

    if lib in included:
        return

    if path is not None:
        included[lib] = path
        scriptq.execute(path)
        return

    if local_tunel != None:
        # Local tunel is special technique for use licant 
        # with python packages. Local tunel create link 
        # for setup.py can find sources by relative path. 

        if not os.path.exists(local_tunel[0]):
            # Убеждаемся, что директории до тунеля существуют
            if not os.path.exists(os.path.dirname(local_tunel[0])):
                os.makedirs(os.path.dirname(local_tunel[0]))

            rawdir = os.path.dirname(libs[lib])
            rawbase = os.path.basename(libs[lib])

            if not os.path.exists(local_tunel[0]):
                os.symlink(rawdir, local_tunel[0])

            included[lib] = os.path.join(local_tunel[0], local_tunel[1])
            scriptq.execute(os.path.join(local_tunel[0], local_tunel[1]))
            return

        else:
            included[lib] = os.path.join(local_tunel[0], local_tunel[1])
            scriptq.execute(os.path.join(local_tunel[0], local_tunel[1]))
            return            

    if not lib in libs:
        print(
            "Unregistred library {}. Use licant-config utility or manually edit {} or {} file.".format(
                yellow(lib), yellow(lpath), yellow(gpath)
            )
        )
        exit(-1)

    included[lib] = libs[lib]
    scriptq.execute(libs[lib])


def print_libs(taget, *args):
    if libs is None:
        init()

    keys = sorted(libs.keys())
    for k in keys:
        print("{}: {}".format(k, libs[k]))


libs_target = licant.core.Target(
    tgt="l", deps=[], list=print_libs, actions={"list"}, __help__="Licant libs info"
)

licant.core.core.add(libs_target)
