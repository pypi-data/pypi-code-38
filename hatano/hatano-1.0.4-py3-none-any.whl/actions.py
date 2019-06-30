from hatano.util import Conf
from copy import deepcopy

import sys
import os


def init(args):
    c = Conf()
    if not c.exists():
        proj = args.name
        runtime = args.runtime
        conf = {
                "project": proj,
                "runtime": runtime
                }
        c.write(conf)
        return
    print("Hatano project exists")


def make(_args):
    args = vars(_args)
    typ = args["object"]
    name = args[typ]
    return make_object(name, typ, args)


def make_object(name, typ, args, edit=False):
    if typ == "stage":
        with open(f'requirements-{name}.txt', 'a') as f:
            pass

    c = Conf()
    conf = c.read()

    if name in conf.get(typ, {}) and not edit:
        print(f"{typ} {name} already exists")
        return

    if name not in conf.get(typ, {}) and edit:
        print(f"{typ} {name} doesn't exist")
        return

    if typ not in conf:
        conf[typ] = {}

    if name not in conf[typ]:
        conf[typ][name] = {}

    if typ == "stage":
        attrs = ["source", "bucket", "domain", "cert"]
    elif typ == "function":
        attrs = ["handler", "method", "path"]

    for attr in attrs:
        if args.get(attr):
            conf[typ][name][attr] = args.get(attr)

    c.write(conf)


def remove(_args):
    args = vars(_args)
    typ = args["object"]
    name = args[typ]
    return rm_object(name, typ)


def rm_object(name, typ):
    c = Conf()
    conf = c.read()
    if name in conf.get(typ, {}):
        del conf[typ][name]
    c.write(conf)
    if typ == "stage":
        try:
            os.remove(f"requirements-{name}.txt")
        except Exception as e:
            print(e)


def edit(_args):
    args = vars(_args)
    typ = args["object"]
    name = args[typ]
    return make_object(name, typ, args, edit=True)


def show(args):
    c = Conf()
    print(c.show(), end='')

