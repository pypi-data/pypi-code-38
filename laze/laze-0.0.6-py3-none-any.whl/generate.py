#!/usr/bin/env python3

import os
import re
import sys
import time
import yaml

# try to use libyaml (faster C-based yaml lib),
# fallback to pure python version
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print("laze: warning: using slow python-based yaml loader")
    from yaml import Loader, Dumper

from .deepcopy import deepcopy
from collections import defaultdict
from itertools import chain

from string import Template

import click

from .util import (
    merge,
    listify,
    default_to_regular,
    dict_list_product,
    dump_dict,
    uniquify,
    deep_replace,
    deep_substitute,
    deep_safe_substitute,
    flatten_var,
    flatten_vars,
    static_vars,
    split,
)

from ninja_syntax import Writer
import laze.dl as dl

from laze.common import (
    ParseError,
    InvalidArgument,
    determine_dirs,
    dump_args,
    rel_start_dir,
    write_ninja_build_args_file
)

import laze.mtimelog

from laze.debug import dprint
import laze.constants as const


files_set = set()
short_module_defines = True
global_build_dir = None


def get_data_folder():
    return os.path.join(os.path.dirname(__file__), "data")


def find_import_file(folder):
    for filename in [const.BUILDFILE_NAME, const.PROJECTFILE_NAME]:
        import_file = os.path.join(folder, filename)
        if os.path.isfile(import_file):
            return import_file


def yaml_load(
    filename, path=None, defaults=None, parent=None, imports=None, import_root=None
):
    def do_include(data):
        includes = listify(data.get("include"))
        _import_root = data.get("_import_root")
        for include in includes:
            _data = (
                yaml_load(
                    os.path.join(os.path.dirname(filename), include),
                    path,
                    parent=filename,
                    imports=imports,
                    import_root=_import_root,
                )[0]
                or {}
            )
            _data.pop("ignore", None)
            if "template" in _data:
                raise ParseError(
                    "template statement in included file currently not supported!"
                )
            merge(_data, data, override=True)
            data = _data

        data.pop("include", None)
        return data

    def remember_imports():
        _imports = listify(data.get("import"))
        for _import in _imports:
            imports.append((filename, _import))

    path = path or ""

    # print("yaml_load(): loading %s with relpath %s" % (filename, path))

    files_set.add(filename)
    if parent is None:
        imports = []

    try:
        with open(filename, "r") as f:
            datas = yaml.load_all(f.read(), Loader=Loader)
    except FileNotFoundError as e:
        msg = "laze: error: cannot find %s%s" % (
            filename,
            " (included by %s)" % parent if parent else "",
        )
        raise ParseError(msg) from e

    res = []
    try:
        for data in datas:
            if import_root is not None:
                data["_import_root"] = import_root

            remember_imports()

            data_defaults = data.get("defaults", {})

            _defaults = defaults
            if _defaults:
                _defaults = deepcopy(_defaults)
                if data_defaults:
                    merge(_defaults, data_defaults)
            else:
                _defaults = data_defaults

            def merge_defaults(data, _defaults):
                if _defaults:
                    # print("yaml_load(): merging defaults, base:    ", data)
                    # print("yaml_load(): merging defaults, defaults:", _defaults)
                    for defaults_key in _defaults.keys():
                        if defaults_key not in data:
                            continue
                        data_val = data.get(defaults_key)
                        defaults_val = _defaults[defaults_key]
                        if type(data_val) == list:
                            for entry in data_val:
                                merge(entry, deepcopy(defaults_val), join_lists=True)
                        else:
                            # print("yaml_load(): merging defaults,", data_val)
                            if data_val == None:
                                data_val = {}
                                data[defaults_key] = data_val
                            merge(data_val, defaults_val, override=False, join_lists=True)
                    # print("yaml_load(): merging defaults, result:  ", data)

            merge_defaults(data, _defaults)

            template = data.pop("template", None)

            if template:
                result = []
                i = 0
                for repl in dict_list_product(template):
                    _data = deepcopy(data)
                    _data["_relpath"] = path
                    _data = deep_replace(_data, repl)
                    _data = do_include(_data)
                    _data["template_instance"] = repl
                    _data["template_instance_num"] = i

                    result.append(_data)
                    i += 1
                res.extend(result)
            else:
                data = do_include(data)
                data["_relpath"] = path
                res.append(data)
                for subdir in listify(data.get("subdirs", [])):
                    relpath = os.path.join(path, subdir)
                    res.extend(
                        yaml_load(
                            os.path.join(relpath, const.BUILDFILE_NAME),
                            path=relpath,
                            defaults=_defaults,
                            parent=filename,
                            imports=imports,
                            import_root=import_root,
                        )
                    )
    except yaml.parser.ParserError as e:
        print(filename, e)
        sys.exit(1)

    if parent is None:
        while imports:
            # print("IMPORTS:", imports)
            imported_list = []
            imports_as_dicts = []

            # unify all imports so they have the form
            # (importer_filename, import name or URL, possible dictionary)
            for _import_tuple in imports:
                importer_filename, _import = _import_tuple
                if type(_import) is dict:
                    for k, v in _import.items():
                        imports_as_dicts.append((importer_filename, k, v))
                else:
                    imports_as_dicts.append((importer_filename, _import, {}))

            for _import_tuple in imports_as_dicts:
                importer_filename, name, import_dict = _import_tuple

                url = import_dict.get("url")
                version = import_dict.get("version")
                folder_override = import_dict.get("folder_override")

                if url is None:
                    url = name
                    name = os.path.basename(name)

                if url.startswith("$laze/"):
                    dl_source = {
                        "local": {
                            "path": os.path.join(
                                get_data_folder(), url[len("$laze/") :]
                            )
                        }
                    }
                else:
                    dl_source = {"git": {"url": url}}

                global global_build_dir
                folder = os.path.join(global_build_dir, "imports", name)
                if version is not None:
                    dl_source["git"]["commit"] = version
                    folder = os.path.join(folder, version)
                else:
                    folder = os.path.join(folder, "latest")

                if folder_override is None:
                    dl.add_to_queue(dl_source, folder)
                else:
                    folder = folder_override

                subdir = import_dict.get("subdir")
                if subdir is not None:
                    folder = os.path.join(folder, subdir)

                imported_list.append((name, importer_filename, folder))

            dl.start()

            imports = []
            for imported in imported_list:
                # print("YY", imported_list)
                name, importer_filename, folder = imported
                import_file = find_import_file(folder)
                if import_file == None:
                    print(
                        "laze: error: folder %s (imported by %s) doesn't contain any laze build file."
                        % (folder, importer_filename)
                    )
                    sys.exit(1)

                res.extend(
                    yaml_load(
                        import_file,
                        path=folder,
                        parent=importer_filename,
                        imports=imports,
                        import_root=folder,
                    )
                )

    return res


class Declaration(object):
    def __init__(self, **kwargs):
        self.args = kwargs
        self.relpath = self.args.get("_relpath")
        self.root = self.args.get("_import_root") or "."
        self.override_source_location = None

        _vars = self.args.get("vars", {})
        for key, value in _vars.items():
            _vars[key] = listify(value)
        self.args["vars"] = _vars

    def post_parse():
        pass

    def locate_source(self, filename=None):
        if filename == None:
            filename = ""
        if self.override_source_location:
            res = os.path.join(self.override_source_location, filename)
        else:
            res = os.path.join(self.relpath, filename)
        return res.rstrip("/") or "."


class Context(Declaration):
    map = {}

    def __init__(self, add_to_map=True, **kwargs):
        super().__init__(**kwargs)

        self.name = kwargs.get("name")
        self.parent = kwargs.get("parent")
        self.children = []
        self.modules = {}
        self.vars = None
        self.tools = None

        self.var_options = None

        self.bindir = self.args.get(
            "bindir", os.path.join(self.args.get("_builddir"), "bin", self.name)
        )

        if add_to_map:
            Context.map[self.name] = self

        self.disabled_modules = set(kwargs.get("disable_modules", []))

        depends(self.name)
        # print("CONTEXT", s.name)

    def __repr__(self, nest=False):
        res = "Context(" if not nest else ""
        res += '"' + self.name + '"'
        if self.parent:
            res += "->" + self.parent.__repr__(nest=True)
        else:
            res += ")"
        return res

    def post_parse():
        for name, context in Context.map.items():
            if context.parent:
                context.parent = Context.map[context.parent]
                context.parent.children.append(context)
                depends(context.parent.name, name)


    def vars_substitute(self, _vars):
        _dict = {
            "relpath": self.relpath.rstrip("/") or ".",
            "root": self.root.rstrip("/") or ".",
        }

        return deep_safe_substitute(_vars, _dict)

    def process_var_options(self, _vars):
        def apply_var_options(opts, data):
            """ interpret smart options.

            Use like e.g.,
                var_options:
                  includes:
                    prefix: -I

            to get a list of path names joined as C include arguments.
            [ "include/foo", "include/bar" ] -> "-Iinclude/foo -Iinclude/bar"
            """

            joiner = opts.get("joiner", " ")
            prefix = opts.get("prefix", "")
            suffix = opts.get("suffix", "")
            start = opts.get("start", "")
            end = opts.get("end", "")

            return (
                start
                + joiner.join([prefix + entry + suffix for entry in data])
                + end
            )

        var_opts = self.get_var_options()

        tmp = None
        for key, value in _vars.items():
            opts = var_opts.get(key)
            if opts is None:
                continue

            if tmp is None:
                tmp = {}

            tmp[key] = apply_var_options(opts, listify(value))

        if tmp:
            _vars.update(tmp)

        return _vars

    def get_var_options(self):
        if self.var_options is not None:
            pass

        else:
            own_opts = self.args.get("var_options")
            if self.parent:
                popts = deepcopy(self.parent.get_var_options())
                if own_opts is not None:
                    popts.update(own_opts)
                self.var_options = popts
            else:
                self.var_options = own_opts or {}

        return self.var_options

    def get_module(self, module_name):
        #        print("get_module()", s, s.modules.keys())
        if module_name in self.disabled_modules:
            print("DISABLED_MODULE", self.name, module_name)
            return None

        module = self.modules.get(module_name)
        if not module and self.parent:
            module = self.parent.get_module(module_name)
        return module

    def get_vars(self):
        if self.vars:
            pass
        elif self.parent:
            _vars = {}
            pvars = self.parent.get_vars()
            merge(_vars, deepcopy(pvars), override=True, change_listorder=False)
            own_vars = self.vars_substitute(self.args.get("vars", {}))
            merge(_vars, own_vars, override=True, change_listorder=False)

            self.vars = _vars
        else:
            self.vars = self.vars_substitute(self.args.get("vars", {}))

        return self.vars

    def get_tools(self):
        if self.tools:
            pass
        elif self.parent:
            self.tools = deepcopy(self.parent.get_tools())
            self.tools.update(self.args.get("tools", {}))
        else:
            self.tools = self.args.get("tools", {})

        return self.tools

    def get_bindir(self):
        if "$" in self.bindir:
            _dict = defaultdict(lambda: "", name=self.name)
            if self.parent:
                _dict.update(
                    {"parent": self.parent.name, "bindir": self.parent.get_bindir()}
                )

            self.bindir = Template(self.bindir).substitute(_dict)
        return self.bindir

    def get_filepath(self, filename=None):
        if filename is not None:
            return os.path.join(self.get_bindir(), filename)
        else:
            return self.get_bindir()

    def listed(self, _set, empty_val=False):
        if not _set:
            return empty_val
        elif self.name in _set:
            return True
        elif self.parent:
            return self.parent.listed(_set)
        else:
            return False


class Builder(Context):
    pass


class Rule(Declaration):
    rule_var_re = re.compile(r"\${\w+}")
    rule_num = 0
    rule_cached = 0
    rule_map = {}
    rule_name_map = {}
    rule_cache = {}
    file_map = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.args["name"]
        self.cmd = self.args["cmd"]
        self.depfile = self.args.get("depfile")
        self.deps = self.args.get("deps")

        try:
            in_ext = self.args["in"]
            if in_ext in Rule.rule_map:
                print("error: %s extension already taken")
                return
            Rule.rule_map[in_ext] = self
        except KeyError:
            pass

        Rule.rule_name_map[self.name] = self

        self.create_var_list()
        global writer
        self.to_ninja(writer)

    def get_by_extension(filename):
        filename, file_extension = os.path.splitext(filename)
        return Rule.rule_map[file_extension]

    def get_by_name(name):
        return Rule.rule_name_map[name]

    def create_var_list(self):
        _var_names = Rule.rule_var_re.findall(self.cmd)
        seen = {}
        var_names = []
        for name in _var_names:
            if name in seen:
                continue
            name = name[2:-1]
            if not name in {"in", "out"}:
                var_names.append(name)
        print("RULE", self.name, "vars:", var_names)
        self.var_set = set(var_names)

    def to_ninja(self, writer):
        writer.rule(
            self.name,
            self.cmd,
            description="%s ${out}" % self.name,
            deps=self.deps,
            depfile=self.depfile,
        )

    def to_ninja_build(self, writer, _in, _out, _vars=None):
        _vars = _vars or {}
        #print("RULE", self.name, _in, _out, _vars)

        # filter _vars by variable names from self.var_set
        #vars = { k: v for k, v in _vars.items() if k in self.var_set }

        # create a cache key from everything but the output
        cache_key = hash(
            "rule:%s in:%s vars:%s" % (self.name, _in, hash(frozenset(_vars.items())))
        )

        Rule.rule_num += 1
        try:
            cached = Rule.rule_cache[cache_key]
            # print("laze: %s using cached %s for %s %s" % (s.name, cached, _in, _out))
            Rule.rule_cached += 1
            return cached

        except KeyError:
            Rule.rule_cache[cache_key] = _out
            # print("laze: NOCACHE: %s %s ->  %s" % (s.name, _in, _out), vars)
            writer.build(outputs=_out, rule=self.name, inputs=_in, variables=_vars)
            return _out


@static_vars(map={})
def depends(name, deps=None):
    depends.map.setdefault(name, set()).update(listify(deps))


def list_remove(_list):
    if _list:
        remove = set()
        for entry in _list:
            if entry[0] == "-":
                remove.add(entry)
                remove.add(entry[1:])

        if remove:
            _set = frozenset(_list)
            for entry in _set & remove:
                _list.remove(entry)


_in = "/-"
_out = "__"

transtab = str.maketrans(_in, _out)


class Module(Declaration):
    class NotAvailable(Exception):
        def __init__(self, context, module, dependency):
            self.context = context
            self.module = module
            self.dependency = dependency

        def __str__(self):
            return '%s in %s depends on unavailable module "%s"' % (
                self.module,
                self.context,
                self.dependency,
            )

    list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Module.list.append(self)
        self.name = self.args.get("name")
        if not self.name:
            if self.relpath:
                self.name = os.path.dirname(self.relpath + "/")
                import_root = self.args.get("_import_root")
                if import_root is not None:
                    self.name = os.path.relpath(self.name, import_root)
                    if self.name == ".":
                        self.name = None

        if not self.name:
            raise InvalidArgument("module missing name")

        self.args["name"] = self.name

        uses = self.args["uses"] = listify(self.args.get("uses"))
        depends = self.args["depends"] = listify(self.args.get("depends"))

        # add optional sources' trigger modules to "uses"
        sources = self.args.get("sources")
        if sources:
            for source in sources:
                if type(source) == dict:
                    for key, value in source.items():
                        # splitting by comma enables multiple deps like "- a,b: file.c"
                        uses.extend(key.split(","))

        list_remove(uses)
        list_remove(depends)

        for name in depends:
            if name.startswith("?"):
                uses.append(name[1:])

        self.context = None
        self.get_nested_cache = {}
        self.export_vars = {}

        self.depends = depends
        self.used = uses
        self.depends_cache = {}
        self.uses_cache = {}
        self.used_deps_cache = {}

    def post_parse():
        for module in Module.list:
            context_name = module.args.get("context", "default")
            context = Context.map.get(context_name)
            if not context:
                print(
                    "laze: error: module %s refers to unknown context %s"
                    % (module.name, context_name)
                )
            module.context = context
            context.modules[module.args.get("name")] = module
            # print("MODULE", module.name, "in", context)
            module.handle_download(module.args.get("download"))

    def handle_download(self, download):
        if download:
            global global_build_dir
            # TODO: check if relpath is appropriate
            dldir = os.path.join(global_build_dir, "dl", self.relpath, self.name)
            print("DOWNLOAD", self.name, download, dldir)

            # handle possibly passed subdir parameter
            if type(download) == dict:
                subdir = download.get("subdir")
                if subdir:
                    dldir = os.path.join(dldir, subdir)

            # make "locate_source()" return filenames in downloaded folder/[subdir/]
            self.override_source_location = dldir

            dl.add_to_queue(download, dldir)

    def get_deps(self, context, resolved=None, unresolved=None):
        if resolved is None:
            try:
                return self.depends_cache[context]
            except KeyError:
                pass

            #print("get_deps()", self.name)

            resolved = []
            unresolved = set()
            recursed = False
        else:
            recursed = True

        unresolved.add(self)

        for dep_name in self.depends:
            # (handle if X is in module_set, depend on Y)
            #if type(dep_name) == dict:
            #    # HANDLE
            #    continue

            if dep_name.startswith("?"):
                dep_name = dep_name[1:]

                dep = context.get_module(dep_name)
                if dep is not None:
                    try:
                        dep.get_deps(context)
                    except Module.NotAvailable:
                        continue
                else:
                    continue
            else:
                dep = context.get_module(dep_name)

                if dep is None:
                    raise Module.NotAvailable(context, self.name, dep_name)

            if dep not in resolved:
                if dep in unresolved:
                    #print("skip dep %s -> %s" %(self.name, dep.name))
                    continue

                dep.get_deps(context, resolved, unresolved)

        resolved.append(self)
        unresolved.discard(self)

        if recursed is False:
            _reversed = uniquify(reversed(resolved))
            self.depends_cache[context] = _reversed
            #print("get_deps() resolved to", self.name, [ x.name for x in _reversed ])
            return _reversed

    def get_used(self, context, module_set):
        try:
            return self.uses_cache[context]
        except KeyError:
            pass

        res = []
        for dep_name in self.used:
            if dep_name in module_set:
                res.append(context.get_module(dep_name))

        self.uses_cache[context] = res
        return res

    def get_used_deps(self, context, module_set, resolved=None, unresolved=None):
        if resolved is None:
            try:
                return self.used_deps_cache[context]
            except KeyError:
                pass
            resolved = []
            unresolved = set()
            recursed = False
        else:
            recursed = True

        unresolved.add(self)

        for dep in chain(self.get_deps(context), self.get_used(context, module_set)):
            if dep not in resolved:
                if dep in unresolved:
                    #print("skip dep %s -> %s" %(self.name, dep.name))
                    continue

                dep.get_used_deps(context, module_set, resolved, unresolved)

        resolved.append(self)
        unresolved.discard(self)

        if recursed is False:
            _reversed = uniquify(reversed(resolved))
            self.used_deps_cache[context] = _reversed
            return _reversed

    def get_vars(self, context):
        vars = self.args.get("vars", {})
        if vars:
            _vars = deepcopy(context.get_vars())
            merge(_vars, vars, override=True)
            _vars = self.vars_substitute(_vars, context)
            return _vars
        else:
            return deepcopy(context.get_vars())

    def get_export_vars(self, context, module_set):
        try:
            return self.export_vars[context]
        except KeyError:
            pass

        vars = {}

        for dep in self.get_used_deps(context, module_set):
            #print("get_export_vars", self.name, dep.name)
            dep_export_vars = dep.args.get("export_vars", {})
            if dep_export_vars:
                dep_export_vars = dep.vars_substitute(dep_export_vars, context)
                merge(vars, dep_export_vars, join_lists=True)

        self.export_vars[context] = vars
        return vars

    def vars_substitute(self, _vars, context):
        _dict = {
            "relpath": self.relpath,
            "root": self.root,
            "srcdir": self.locate_source(""),
        }

        deep_safe_substitute(_vars, _dict)
        return deep_substitute(_vars, flatten_vars(context.get_vars()))

    def uses_all(self):
        return "all" in listify(self.args.get("uses", []))

    def get_defines(self, context, module_set):
        if self.uses_all():
            deps_available = module_set
        else:
            deps_available = set()
            for dep in self.get_used_deps(context, module_set):
                for used in dep.get_used(context, module_set):
                    deps_available.add(used.name)

        dep_defines = []
        for dep_name in sorted(deps_available):
            if short_module_defines:
                dep_name = os.path.basename(dep_name)
            dep_defines.append("-DMODULE_" + dep_name.upper().translate(transtab))
        return dep_defines


rec_dd = lambda: defaultdict(rec_dd)


class App(Module):
    count = 0
    list = []
    global_applist = set()
    global_whitelist = set()
    global_blacklist = set()
    global_tools = rec_dd()  # defaultdict(lambda: dict())
    global_app_per_folder = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: dict()))
    )
    global_apps_data = dict()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.list.append(self)

        self.bindir = self.args.get("bindir", os.path.join("${parent}", "${name}"))

        def _list(self, name):
            return set(listify(self.args.get(name, [])))

        self.whitelist = _list(self, "whitelist")
        self.blacklist = _list(self, "blacklist") | App.global_blacklist
        self.tools = self.args.get("tools", {})

    def post_parse():
        for app in App.list:
            app.build()

    def build(self):
        if App.global_applist and not self.name in App.global_applist:
            return

        appdict = App.global_apps_data[self.name] = {}
        for name, builder in Context.map.items():
            if builder.__class__ != Builder:
                continue

            builderdict = appdict[builder.name] = {}
            if not (
                builder.listed(self.whitelist, empty_val=True)
                and builder.listed(App.global_whitelist, empty_val=True)
            ):
                builderdict["notbuilt_reason"] = "not whitelisted"
                continue

            if builder.listed(self.blacklist):
                builderdict["notbuilt_reason"] = "blacklisted"
                continue

            #
            context = Context(
                add_to_map=False,
                name=self.name,
                parent=builder,
                vars={"builder": name},
                tools=self.tools,
                _relpath=self.relpath,
                _builddir=self.args.get("_builddir")
            )

            #
            context.bindir = self.bindir
            if "$" in context.bindir:
                context.bindir = Template(context.bindir).substitute(
                    {
                        "parent": builder.get_bindir(),
                        "name": self.name,
                        "app": self.name,
                        "builder": name,
                    }
                )
            if context.bindir.startswith("./"):
                context.bindir = os.path.join(self.relpath, context.bindir[2:])

            context_vars = context.get_vars()

            print("laze:  building", self.name, "for", name)

            try:
                modules = self.get_deps(context)
            except Module.NotAvailable as e:
                print(
                    "laze: WARNING: skipping app",
                    self.name,
                    "for builder %s:" % context.parent.name,
                    e,
                )
                builderdict["notbuilt_reason"] = { "dependency missing": {
                    "module": e.module,
                    "missing": e.dependency
                    }}
                continue

            App.count += 1

            module_set = set()
            ## beginning of optional dependencies
            # (if X is in module set, depend on Y)
            # modules_depend_optional = {}
            # for module in modules:
            #     module_set.add(module.name)
            #     _tmp = module.args.get("depends")
            #     if _tmp:
            #         for dep in _tmp:
            #             if type(dep) == dict:
            #                 print("OPTIONAL DEP:", module.name, dep)


            modules_dict = builderdict["modules"] = {}
            for module in modules:
                module_set.add(module.name)
                module_global_vars = module.args.get("global_vars", {})
                module_global_vars = module.vars_substitute(module_global_vars, context)
                if module_global_vars:
                    merge(context_vars, module_global_vars, join_lists=True)

                _sources = module.args.get("sources")
                _deps = module.args.get("depends")
                _uses = module.args.get("uses")

                module_dict = modules_dict[module.name] = {}
                module_dict["context"] = module.context.name

                if _sources:
                    module_dict["sources"] = listify(_sources)
                if _deps:
                    module_dict["deps"] = _deps.copy()
                if _uses:
                    module_dict["uses"] = _uses.copy()
                if module_global_vars:
                    module_dict["global_vars"] = module_global_vars

            builderdict["context vars"] = context_vars

            global writer
            sources = []
            objects = []
            for module in modules:
                module_dict = modules_dict[module.name]
                _sources = listify(module.args.get("sources", []))
                sources = []

                # handle optional sources ("- optional_module: file.c")
                for source in _sources:
                    if source is None:
                        continue
                    if type(source) == dict:
                        for key, value in source.items():
                            # splitting by comma enables multiple deps like "- a,b: file.c"
                            key = set(key.split(","))
                            if not key - module_set:
                                _optional_sources = listify(value)
                                module_dict.setdefault("optional sources used", []).extend(_optional_sources)
                                sources.extend(_optional_sources)
                    else:
                        sources.append(source)

                module_defines = module.get_defines(context, module_set)

                module_vars = module.get_vars(context)

                module_export_vars = module.get_export_vars(context, module_set)
                if module_export_vars:
                    module_export_vars = deepcopy(module_export_vars)
                    merge(
                        module_vars, module_export_vars
                    )
                    module_dict["export_vars"] = module_export_vars

                # add "-DMODULE_<module_name> for each used/depended module
                if module_defines:
                    module_vars = deepcopy(module_vars)
                    cflags = module_vars.setdefault("CFLAGS", [])
                    cflags.extend(module_defines)

                if module_vars:
                    module_dict["vars"] = module_vars

                module_used = module.get_used(context, module_set)
                if module_used:
                    module_dict["used"] = [x.name for x in module_used]

                module_vars = context.process_var_options(module_vars)
                module_vars_flattened = flatten_vars(module_vars)
                for source in sources:
                    source_in = module.locate_source(source)
                    rule = Rule.get_by_extension(source)

                    obj = context.get_filepath(
                        os.path.join(module.relpath, source[:-2] + rule.args.get("out"))
                    )
                    obj = rule.to_ninja_build(writer, source_in, obj, module_vars_flattened)
                    objects.append(obj)
                    # print ( source) # , module.get_vars(context), rule.name)

            link = Rule.get_by_name("LINK")
            try:
                outfile = context.get_filepath(self.args["outfile"])
            except KeyError:
                outfile = context.get_filepath(os.path.basename(self.name)) + ".elf"

            builderdict["outfile"] = outfile

            context_vars = context.process_var_options(context_vars)
            res = link.to_ninja_build(writer, objects, outfile, flatten_vars(context_vars))
            if res != outfile:
                # An identical binary has been built for another Application.
                # As the binary can be considered a final target, create a file
                # symbolic link.
                symlink = Rule.get_by_name("SYMLINK")
                symlink.to_ninja_build(writer, res, outfile)
                builderdict["outfile_real"] = res


            depends(context.parent.name, outfile)
            depends(self.name, outfile)
            depends("%s:%s" % (self.name, name), outfile)

            module_vars["out"] = outfile
            module_vars["relpath"] = self.relpath

            # handle tools
            tools = context.get_tools()
            if tools:
                module_vars_flattened = flatten_vars(module_vars)

                tools_dict = builderdict["tools"] = {}
                for tool_name, spec in tools.items():
                    #dprint(
                    #    "verbose",
                    #    "laze: app %s supports tool %s" % (self.name, tool_name),
                    #)
                    if type(spec) == str:
                        cmd = [str]
                        spec = {}
                    elif type(spec) == list:
                        cmd = spec
                        spec = {}
                    elif type(spec) == dict:
                        cmd = spec["cmd"]
                    else:
                        print("laze: error: app %s tool %s has invalid format.")
                        sys.exit(1)

                    # substitute variables
                    cmd = [
                        Template(command).substitute(module_vars_flattened)
                        for command in cmd
                    ]
                    spec["cmd"] = cmd
                    # spec["target"] = outfile

                    App.global_tools[outfile][tool_name] = spec
                    tools_dict[tool_name] = spec


            App.global_app_per_folder[self.relpath][self.name][builder.name] = outfile


class_map = {
    "context": Context,
    "builder": Builder,
    "rule": Rule,
    "module": Module,
    "app": App,
}


@click.command()
@click.option("--project-file", "-f", type=click.STRING, envvar="LAZE_PROJECT_FILE")
@click.option("--project-root", "-r", type=click.STRING, envvar="LAZE_PROJECT_ROOT")
@click.option("--builders", "-b", multiple=True, envvar="LAZE_BUILDERS")
@click.option("--apps", "-a", multiple=True, envvar="LAZE_APPS")
@click.option(
    "--build-dir", "-B", type=click.STRING, default="build", envvar="LAZE_BUILDDIR"
)
@click.option("--global/--local", "-g/-l", "_global", default=False, envvar="LAZE_GLOBAL")
@click.option("--args-file", "-A", type=click.Path(), envvar="LAZE_ARGS_FILE")
@click.option("--dump-data", "-d", is_flag=True, default=False, envvar="LAZE_DUMP_DATA")
def generate(**kwargs):
    global writer
    global global_build_dir

    args_file = kwargs.get("args_file")
    if args_file:
        # TODO: allow overriding via command line?
        args = yaml.load(open(args_file, "r"))
    else:
        kwargs["apps"] = split(kwargs.get("apps"))
        kwargs["builders"] = split(kwargs.get("builders"))
        args = kwargs

    _global   = args.get("_global")
    apps      = args.get("apps")
    blacklist = args.get("blacklist")
    builders  = args.get("builders")

    start_dir, build_dir, project_root, project_file = determine_dirs(args)
    global_build_dir = build_dir

    os.chdir(project_root)

    args_file = dump_args(build_dir, args)

    App.global_whitelist = set(builders)
    App.global_blacklist = set()  # set(split(list(blacklist or [])))
    App.global_applist = set(apps)

    if not _global:
        _rel_start_dir = rel_start_dir(start_dir, project_root)
        print("laze: generate: local mode in %s" % _rel_start_dir)

    before = time.time()
    try:
        data_list = yaml_load(project_file)
    except ParseError as e:
        print(e)
        sys.exit(1)

    print("laze: loading %i buildfiles took %.2fs" % (len(files_set), time.time() - before))

    ninja_build_file = os.path.join(build_dir, "build.ninja")
    ninja_build_args_file = os.path.join(build_dir, "build-args.ninja")
    ninja_build_file_deps = ninja_build_file + ".d"

    writer = Writer(open(ninja_build_file, "w"))
    writer.variable("builddir", build_dir)

    # create rule for automatically re-running laze if necessary
    write_ninja_build_args_file(ninja_build_args_file, ninja_build_file, ninja_build_file_deps, args_file, build_dir)

    before = time.time()
    # PARSING PHASE
    # create objects
    for data in data_list:
        relpath = data.get("_relpath", "") or "."
        import_root = data.get("_import_root", "")
        for name, _class in class_map.items():
            if (
                (_global is not True)
                and (name == "app")
                and (relpath != _rel_start_dir)
            ):
                continue

            datas = listify(data.get(name, []))
            for _data in datas:
                _data["_relpath"] = relpath
                _data["_builddir"] = build_dir
                _data["_import_root"] = import_root
                _class(**_data)

    no_post_parse_classes = {Builder}

    # POST_PARSING PHASE
    for name, _class in class_map.items():
        if _class in no_post_parse_classes:
            continue
        _class.post_parse()

    print("laze: processing buildfiles took %.2fs" % (time.time() - before))
    print("laze: configured %s applications" % App.count)
    if Rule.rule_num:
        print(
            "laze: cached: %s/%s (%.2f%%)"
            % (Rule.rule_cached, Rule.rule_num, Rule.rule_cached * 100 / Rule.rule_num)
        )

    for dep, _set in depends.map.items():
        writer.build(rule="phony", outputs=dep, inputs=list(_set))

    ## dump some data structures that build will pick up
    dump_dict((build_dir, "laze-tools"), App.global_tools)
    dump_dict((build_dir, "laze-app-per-folder"), App.global_app_per_folder)

    ## optionally dump info struct
    if args.get("dump_data"):
        print("laze: dumping data")
        dump_dict((build_dir, "laze-data"), App.global_apps_data)

    laze.mtimelog.write_log(os.path.join(build_dir, "laze-files.mp"), files_set)
    with open(ninja_build_file_deps, "w") as f:
        f.write(ninja_build_args_file + ": " + " ".join(files_set))

    # download external sources
    dl.start()
