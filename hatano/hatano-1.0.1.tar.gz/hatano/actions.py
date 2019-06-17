from hatano.util import Conf
from copy import deepcopy

import sys


def init(args):
    c = Conf()
    if not c.exists():
        try:
            proj_name = input("Project name: ")
        except KeyboardInterrupt:
            sys.exit("Aborted")
        conf = {
                "project": proj_name,
                }
        c.write(conf)
        return
    print("Hatano project exists")


def add(args):
    if args.object == "stage":
        return add_stage(args)

    elif args.object == "function":
        return add_function(args)


def add_stage(args):
    stage = args.stage
    copy = args.copy
    source = args.source
    runtime = args.runtime
    domain = args.domain
    cert = args.cert

    with open(f'requirements-{stage}.txt', 'a') as f:
        pass

    c = Conf()
    conf = c.read()
    if stage in conf.get("stages", {}):
        print(f"Stage {stage} already exists")
        return

    if copy and copy in conf.get("stages", {}):
        conf["stages"][stage] = deepcopy(conf["stages"][copy])
        c.write(conf)
        return

    if "stages" not in conf:
        conf["stages"] = {}

    conf["stages"][stage] = {
            "functions": {},
            "source": source,
            "runtime": runtime}
    if domain:
        conf["stages"][stage]["domain"] = domain
    if cert:
        conf["stages"][stage]["cert"] = cert

    c.write(conf)


def add_function(args):
    stage = args.stage
    c = Conf()
    conf = c.read()
    if stage not in conf.get("stages", {}):
        add_stage(stage)
    conf = c.read()
    if "functions" not in conf["stages"].get(stage, {}):
        conf["stages"][stage]["functions"] = {}
    func = {
            "handler": args.handler,
            "method": args.method,
            "path": args.path}
    conf["stages"][stage]["functions"][args.name] = func
    c.write(conf)


def remove(args):
    if args.object == "stage":
        return rm_stage(args.stage)

    elif args.object == "function":
        return rm_function(args)


def rm_stage(stage):
    c = Conf()
    conf = c.read()
    if "stages" in conf and stage in conf["stages"]:
        del conf["stages"][stage]
    c.write(conf)


def rm_function(args):
    name = args.function
    stage = args.stage
    c = Conf()
    conf = c.read()
    if "stages" in conf and stage in conf["stages"]:
        if name in conf["stages"][stage].get("functions", {}):
            del conf["stages"][stage]["functions"][name]
    c.write(conf)

def edit(args):
    if args.object == "stage":
        return edit_stage(args)

    elif args.object == "function":
        return edit_function(args)


def edit_stage(args):
    stage = args.stage
    copy = args.copy
    source = args.source
    runtime = args.runtime
    domain = args.domain
    cert = args.cert

    c = Conf()
    conf = c.read()
    if stage not in conf.get("stages", {}):
        print(f"Stage {stage} does not exist")
        return

    if copy and copy in conf.get("stages", {}):
        conf["stages"][stage] = deepcopy(conf["stages"][copy])
        c.write(conf)
        return

    if source:
        conf["stages"][stage]["source"] = source
    if runtime:
        conf["stages"][stage]["runtime"] = runtime
    if domain:
        conf["stages"][stage]["domain"] = domain
    if cert:
        conf["stages"][stage]["cert"] = cert


    c.write(conf)


def edit_function(args):
    stage = args.stage
    c = Conf()
    conf = c.read()

    if stage not in conf.get("stages", {}):
        print(f"Stage {stage} does not exist")
        return

    conf = c.read()
    if "functions" not in conf["stages"].get(stage, {}):
        print(f"No functions defined in stage {stage}")
        return

    if args.name not in conf["stages"][stage]["functions"]:
        print(f"Function {args.name} not defined in stage {stage}")
        return

    func = conf["stages"][stage]["functions"][args.name]
    if args.handler:
        func["handler"] = args.handler
    if args.method:
        func["method"] = args.method
    if args.path:
        func["path"] = args.path

    conf["stages"][stage]["functions"][args.name] = func
    c.write(conf)


def show(args):
    c = Conf()
    print(c.show(), end='')

