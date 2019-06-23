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


def make(args):
    if args.object == "stage":
        return make_stage(args)

    elif args.object == "function":
        return make_function(args)


def make_stage(_args, edit=False):
    args = vars(_args)
    stage = args["stage"]

    with open(f'requirements-{stage}.txt', 'a') as f:
        pass

    c = Conf()
    conf = c.read()

    if stage in conf.get("stage", {}) and not edit:
        print(f"Stage {stage} already exists")
        return

    if stage not in conf.get("stage", {}) and edit:
        print(f"Stage {stage} doesn't exist")
        return

    if "stage" not in conf:
        conf["stage"] = {}

    if stage not in conf["stage"]:
        conf["stage"][stage] = {}

    for key in ["source", "bucket", "domain", "cert"]:
        if args[key]:
            conf["stage"][stage][key] = args[key]

    c.write(conf)


def make_function(args):
    c = Conf()
    conf = c.read()
    if "function" not in conf:
        conf["function"] = {}
    func = {
            "handler": args.handler,
            "method": args.method,
            "path": args.path}
    conf["function"][args.function] = func
    c.write(conf)


def remove(_args):
    c = Conf()
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

def edit(args):
    if args.object == "stage":
        return make_stage(args, edit=True)

    elif args.object == "function":
        return edit_function(args)




def edit_function(args):
    stage = args.stage
    c = Conf()
    conf = c.read()

    if stage not in conf.get("stage", {}):
        print(f"Stage {stage} does not exist")
        return

    conf = c.read()
    if "function" not in conf["stage"].get(stage, {}):
        print(f"No functions defined in stage {stage}")
        return

    if args.name not in conf["stage"][stage]["function"]:
        print(f"Function {args.name} not defined in stage {stage}")
        return

    func = conf["stage"][stage]["function"][args.name]
    if args.handler:
        func["handler"] = args.handler
    if args.method:
        func["method"] = args.method
    if args.path:
        func["path"] = args.path

    conf["stage"][stage]["function"][args.name] = func
    c.write(conf)


def show(args):
    c = Conf()
    print(c.show(), end='')

