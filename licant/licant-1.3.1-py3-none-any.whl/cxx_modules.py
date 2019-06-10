# coding: utf-8

from licant.modules import mlibrary
from licant.cxx_make import host_binutils, binutils
from licant.util import red, yellow, cxx_read_depends

import os
import licant.util as gu
import licant.make

import glob
import queue


class solver:
    def __init__(self, type, merge, include, default):
        self.type = type
        self.merge = merge
        self.include = include
        self.default = default


def base(base, local, solver, tbase, tlocal):
    return base


def local(base, local, solver, tbase, tlocal):
    if local is None:
        return solver.default
    return local


def concat(base, local, solver, tbase, tlocal):
    if local is None:
        local = []
    if base is None:
        base = []
    return base + local


def strconcat(base, local, solver, tbase, tlocal):
    if local is None:
        return base
    return base + " " + local


def concat_add_srcdir(base, local, solver, tbase, tlocal):
    if local is None:
        local = []
    else:
        if "srcdir" in tlocal.opts:
            srcdir = tlocal.opts["srcdir"]
        else:
            srcdir = ""

        local = list(
            map(
                lambda p: os.path.join(
                    tlocal.opts["__dir__"], srcdir, os.path.expanduser(p)
                ),
                local,
            )
        )
    # print(base + local)
    return base + local


def local_add_srcdir(base, local, solver, tbase, tlocal):
    if "srcdir" in tlocal.opts:
        srcdir = tlocal.opts["srcdir"]
    else:
        srcdir = ""
    if isinstance(local, type("str")):
        local = [local]
    if local is None:
        return []
    return list(
        map(
            lambda p: os.path.join(
                tlocal.opts["__dir__"], srcdir, os.path.expanduser(p)
            ),
            local,
        )
    )


def concat_add_locdir(base, local, solver, tbase, tlocal):
    if local is None:
        return base

    if isinstance(local, type("str")):
        local = [local]
    local = list(
        map(
            lambda p: os.path.join(tlocal.opts["__dir__"], os.path.expanduser(p)), local
        )
    )
    return base + local


def concat_add_locdir_second(base, local, solver, tbase, tlocal):
    """Добавить локальный путь ко всем вторым элементам локального массива. 
    Для поддержки локальных заголовков."""
    if local is None:
        return base
    local = [(pl[0], os.path.join(tlocal.opts["__dir__"], pl[1])) for pl in local]
    return base + local


def local_if_exist(base, local, solver, tbase, tlocal):
    return base if local is None else local


def concat_to_submodule(base, local, solver, tbase, tlocal):
    if local is None:
        local = []
    if base is None:
        base = []
    lm = [licant.modules.submodule(l) for l in local]
    return base + lm


cxx_module_field_list = {
    #                                       # merge                     #include                    #default
    "srcdir": solver("str", local, base, "."),
    "objects": solver("list", local_add_srcdir, concat_add_srcdir, []),
    "sources": solver("list", local_add_srcdir, concat_add_srcdir, []),
    "moc": solver("list", local_add_srcdir, concat_add_srcdir, []),
    "libs": solver("list", concat, concat, []),
    "target": solver("str", local_if_exist, base, "target"),
    "include_paths": solver("list", concat_add_locdir, concat_add_locdir, []),
    "cxxstd": solver("str", local_if_exist, local_if_exist, "c++14"),
    "ccstd": solver("str", local_if_exist, local_if_exist, "c11"),
    "cxx_flags": solver("str", strconcat, strconcat, ""),
    "cc_flags": solver("str", strconcat, strconcat, ""),
    "ld_flags": solver("str", strconcat, strconcat, ""),
    "modules": solver("list", local, concat, []),
    "type": solver("str", local, base, "objects"),
    "builddir": solver("str", local_if_exist, base, "build"),
    "binutils": solver("binutils", local_if_exist, base, host_binutils),
    "include_modules": solver("list", concat_to_submodule, base, []),
    "defines": solver("list", concat, concat, []),
    "ldscripts": solver("list", concat_add_locdir, concat_add_locdir, []),
    "local_headers": solver(
        "list", concat_add_locdir_second, concat_add_locdir_second, []
    ),
    "mdepends": solver("list", local, base, []),
}


class CXXModuleOptions:
    def __getitem__(self, key):
        return self.opts[key]

    def check(self):
        for k, v in self.opts.items():
            if not k in licant.modules.special:
                if not k in self.table:
                    print("Unresolved option: {}".format(red(k)))
                    exit(-1)

                if v.__class__.__name__ != self.table[k].type:
                    print(
                        "Option should be object of {}: {}".format(
                            yellow(self.table[k].type), red(k)
                        )
                    )
                    exit(-1)

    def set_default_if_empty(self, table=cxx_module_field_list):
        for k in table:
            if not k in self.opts:
                self.opts[k] = table[k].default

    def merge(self, other, fnc):
        resopts = {}
        for k, v in self.opts.items():

            base = self.opts[k]
            if k in other.opts:
                local = other.opts[k]
            else:
                local = None

            func = getattr(self.table[k], fnc)
            resopts[k] = func(base, local, self.table[k], self, other)

        return CXXModuleOptions(**resopts)

    def __init__(self, table=cxx_module_field_list, **kwargs):
        self.opts = kwargs
        self.table = table
        self.check()

    def __str__(self):
        return str(self.opts)


def cxx_options_from_modopts(modopts):
    cxxstd = "-std=" + modopts["cxxstd"]
    ccstd = "-std=" + modopts["ccstd"]

    cxx_flags = cxxstd + " " + modopts["cxx_flags"]
    cc_flags = ccstd + " " + modopts["cc_flags"]

    ld_srcs_add = "".join([" -l" + l for l in modopts["libs"]])

    return licant.cxx_make.options(
        binutils=modopts["binutils"],
        include_paths=modopts["include_paths"],
        cc_flags=cc_flags,
        cxx_flags=cxx_flags,
        defines=modopts["defines"],
        ldscripts=modopts["ldscripts"],
        ld_flags=modopts["ld_flags"],
        ld_srcs_add=ld_srcs_add,
    )


def build_paths(srcs, opts, ext):
    objs = []
    for s in srcs:
        if os.path.isabs(s):
            objs.append(opts.opts["builddir"] + gu.changeext(s, ext))
        else:
            objs.append(
                os.path.normpath(
                    os.path.join(
                        opts.opts["builddir"], gu.changeext(s, ext).replace("..", "__")
                    )
                )
            )
    return objs


def sources_paths(opts):
    ret = []
    for s in opts["sources"]:
        if "*" in s:
            ret.extend(glob.glob(s))
        else:
            ret.append(s)
    return ret


def moc_paths(opts):
    ret = []
    for s in opts["moc"]:
        if "*" in s:
            ret.extend(glob.glob(s))
        else:
            ret.append(s)
    return ret


def link_objects(srcs, objs, deps, cxxopts, adddeps):

    for s, o, d in zip(srcs, objs, deps):
        if not s in licant.core.core.targets:
            licant.make.source(s)

        headers = cxx_read_depends(d)
        force = headers is None
        if headers is None:
            headers = []
        else:
            for h in headers:
                if h not in licant.core.core.targets:
                    licant.make.source(h)

        licant.cxx_make.depend(
            src=s, tgt=d, opts=cxxopts, deps=[s] + adddeps + headers, force=force
        )
        licant.cxx_make.object(
            src=s, tgt=o, opts=cxxopts, deps=[s, d] + adddeps + headers
        )


def link_moc(mocs, srcs, cxxopts, adddeps):
    for m, s in zip(mocs, srcs):
        licant.make.source(m)
        licant.cxx_make.moc(src=m, tgt=s, opts=cxxopts, deps=[m] + adddeps)


def executable(srcs, opts):
    cxxopts = cxx_options_from_modopts(opts)
    licant.cxx_make.executable(tgt=opts["target"], srcs=srcs, opts=cxxopts)
    return opts["target"]


def dynlib(srcs, opts):
    cxxopts = cxx_options_from_modopts(opts)
    licant.cxx_make.dynamic_library(tgt=opts["target"], srcs=srcs, opts=cxxopts)
    return opts["target"]


def virtual(srcs, opts):
    licant.core.target(tgt=opts["target"], deps=srcs)
    return opts["target"]


def collect_modules(mod):
    # Альтернативная система модулей.
    mdepends_default = queue.Queue()
    mdepends = dict()

    class SortKey:
        def __init__(self):
            self.sortkey = 0

        def __call__(self, mod):
            mod.__sortkey = self.sortkey
            self.sortkey += 1

    setsortkey = SortKey()

    def collect_modules(mod):
        if licant.core.core.runtime["trace"]:
            print("trace: collect_modules( {} )".format(mod.name))

        for md in mod.opts["mdepends"]:
            if isinstance(md, str):
                if md in mdepends:
                    continue

                mdepends_default.put(md)

            elif isinstance(md, tuple):
                nmod = mlibrary.get(md[0], md[1])

                if md[0] in mdepends and mdepends[md[0]] is not nmod:
                    licant.error(
                        "This module added early and it's different: mod:{} now:{} early:{}".format(
                            licant.util.yellow(nmod.name),
                            licant.util.yellow(nmod.impl),
                            licant.util.yellow(mdepends[md[0]].impl),
                        )
                    )

                mdepends[md[0]] = nmod
                setsortkey(nmod)

                if "mdepends" in nmod.opts:
                    # Сразу же выполняем обход по данному модулю
                    collect_modules(nmod)

            else:
                licant.error("Very strange mpdepend")

    if "mdepends" in mod.opts:
        collect_modules(mod)

    while not mdepends_default.empty():
        name = mdepends_default.get()
        defmod = mlibrary.get_default(name)

        mdepends[name] = defmod
        setsortkey(defmod)

        if "mdepends" in defmod.opts:
            collect_modules(defmod)

    return [
        mdepends[x]
        for x in sorted(mdepends, key=lambda x: mdepends[x]._SortKey__sortkey)
    ]


def prepare_targets(name, impl=None, **kwargs):
    opts = CXXModuleOptions(**kwargs)
    opts.set_default_if_empty()

    def modmake(name, impl, baseopts):
        mod = mlibrary.get(name, impl)

        moddir = os.path.dirname(mod.script)

        modopts = CXXModuleOptions(**mod.opts)
        locopts = baseopts.merge(modopts, "merge")

        adddeps = []  # mod.stack

        # Проходим по include_modules, рекурсивно формируем локальные опции.
        def include_modules(locopts, lst):
            retopts = locopts
            for simod in lst:
                imod = mlibrary.get(simod.name, simod.impl)
                retopts = retopts.merge(imod, "include")

                if "include_modules" in imod.opts:
                    retopts = include_modules(retopts, imod.opts["include_modules"])

            return retopts

        locopts = include_modules(locopts, locopts["include_modules"])

        # Система модулей mdepends
        for imod in collect_modules(mod):
            locopts = locopts.merge(imod, "include")

        local_headers_targets = []
        if len(locopts["local_headers"]):
            locopts["include_paths"].append(locopts["builddir"] + "/__LOCAL_HEADERS__/")
            for pair in locopts["local_headers"]:
                licant.make.source(pair[1])
                tgtpath = os.path.join(
                    locopts["builddir"], "__LOCAL_HEADERS__", pair[0]
                )
                licant.make.copy(src=pair[1], tgt=tgtpath)

                local_headers_targets.append(tgtpath)

        licant.make.fileset(name + "__local_headers__", local_headers_targets)
        adddeps.append(name + "__local_headers__")

        cxxopts = cxx_options_from_modopts(locopts)

        locsrcs = sources_paths(locopts)
        locobjs = build_paths(locsrcs, locopts, "o")
        locdeps = build_paths(locsrcs, locopts, "d")

        if len(locopts["moc"]) != 0:
            locmoc = moc_paths(locopts)
            locmoccxx = build_paths(locmoc, locopts, "h.cxx")
            locmocobjs = build_paths(locmoc, locopts, "h.cxx.o")
            locmocdeps = build_paths(locmoc, locopts, "h.cxx.d")
            link_moc(locmoc, locmoccxx, cxxopts, adddeps)

            locsrcs.extend(locmoccxx)
            locobjs.extend(locmocobjs)
            locdeps.extend(locmocdeps)

        link_objects(locsrcs, locobjs, locdeps, cxxopts, adddeps)

        if len(locopts["objects"]) != 0:
            for t in locopts["objects"]:
                licant.make.source(t)
            locobjs.extend(locopts["objects"])

        submodules_results = []
        # print(locopts["modules"])
        for smod in locopts["modules"]:
            submodules_results += modmake(smod.name, smod.impl, locopts)

        if locopts["type"] == "application":
            return ([executable(locobjs + submodules_results, locopts)], locopts)
        if locopts["type"] == "shared_library":
            return ([dynlib(locobjs + submodules_results, locopts)], locopts)
        elif locopts["type"] == "objects":
            return (locobjs + submodules_results, locopts)
        else:
            print("Wrong type of assemble: {}", gu.red(locopts["type"]))
            exit(-1)

    res, locopts = modmake(name, impl, opts)
    return (res, locopts)


def task(name, target, impl, type, **kwargs):
    if type != "objects":
        if target is None or target == name:
            target = "./" + name
        licant.modules.module(name, impl=impl, type=type, target=target, **kwargs)
    else:
        licant.modules.module(name, impl=impl, type=type, **kwargs)
    ret, opts = prepare_targets(name)
    licant.make.fileset(tgt=name, targets=ret, finalopts=opts)
    return ret


def application(name, target=None, impl=None, type="application", **kwargs):
    return task(name, target, impl, type, **kwargs)


def shared_library(name, target=None, impl=None, type="shared_library", **kwargs):
    return task(name, target, impl, type, **kwargs)


def objects(name, target=None, impl=None, type="objects", **kwargs):
    return task(name, target, impl, type, **kwargs)


def print_collect_list(target, *args):
    if len(args) > 0:
        name = args[0]
    else:
        print("You should specify target name")
        return 
    for m in sorted(collect_modules(mlibrary.get(name)), key=lambda x: x.name):
        if hasattr(m, "impl"):
            print("{}:{}".format(m.name, m.impl))
        else:
            print(m.name)


def print_finalopts(target, *args):
    if len(args) > 0:
        name = args[0]
    else:
        name = licant.cli.default_target
    print(licant.core.core.get(name).finalopts)


modules_target = licant.core.Target(
    tgt="cxxm",
    deps=[],
    collect_modules=print_collect_list,
    finalopts=print_finalopts,
    actions={"collect_modules", "finalopts"},
    __help__="Info about collected modules",
)

licant.core.core.add(modules_target)
