# coding: utf-8

import licant.util
import threading
import types
import inspect
from enum import Enum
import re


class WrongAction(Exception):
    pass


class NoneDictionary(dict):
    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, idx):
        try:
            return dict.__getitem__(self, idx)
        except:
            return None


class Core:
    def __init__(self):
        self.targets = {}
        self.help_showed_targets = []
        self.runtime = NoneDictionary()

    def add(self, target):
        """Add new target"""
        target.core = self
        self.targets[target.tgt] = target

        if target.__help__ is not None:
            self.help_showed_targets.append(target)

    def get(self, tgt):
        """Get target object"""
        if tgt in self.targets:
            return self.targets[tgt]
        licant.util.error("unregistred target " + licant.util.yellow(tgt))

    def subtree(self, root):
        """Construct Subtree accessor for root target"""
        return SubTree(self, root)

    def depends_as_set(self, tgt, incroot=True):
        """"""
        res = set()
        if incroot:
            res.add(tgt)

        target = self.get(tgt)

        for d in target.deps:
            if not d in res:
                res.add(d)
                subres = self.depends_as_set(d)
                res = res.union(subres)
        return sorted(res)


# Объект ядра с которым библиотеки работают по умолчанию.
core = Core()


class SubTree:
    def __init__(self, core, root):
        self.root = root
        self.core = core
        self.depset = core.depends_as_set(root)

    #    def update(self):
    #        SubTree.__init__(self, root)

    def invoke_foreach(self, ops, cond=licant.util.always_true):
        if core.runtime["debug"]:
            print("FOREACH(root={}, ops={}, cond={})".format(self.root, ops, cond))

        sum = 0
        ret = None

        for d in self.depset:
            target = self.core.get(d)
            if cond(target):
                ret = target.invoke(ops)

            if ret is not None:
                sum += 1

        return sum

    def __generate_rdepends_lists(self, targets):
        for t in targets:
            t.rdepends = []
            t.rcounter = 0

        for t in targets:
            for dname in t.deps:
                dtarget = self.core.get(dname)
                dtarget.rdepends.append(t.tgt)

    def reverse_recurse_invoke_single(
        self, ops, threads=None, cond=licant.util.always_true
    ):
        if core.runtime["trace"]:
            print(
                "SINGLETHREAD MODE(root={}, ops={}, cond={})".format(
                    self.root, ops, cond
                )
            )
        targets = [self.core.get(t) for t in self.depset]

        self.__generate_rdepends_lists(targets)

        works = licant.util.queue()

        for t in targets:
            if t.rcounter == len(t.deps):
                works.put(t)

        while not works.empty():
            w = works.get()

            if cond(w):
                ret = w.invoke(ops)
                if ret is False:
                    print(licant.util.red("runtime error"))
                    exit(-1)

            for r in [self.core.get(t) for t in w.rdepends]:
                r.rcounter = r.rcounter + 1
                if r.rcounter == len(r.deps):
                    works.put(r)

    def reverse_recurse_invoke_threads(
        self, ops, threads, cond=licant.util.always_true
    ):
        if core.runtime["trace"]:
            print(
                "MULTITHREAD MODE(root={}, threads={}, ops={}, cond={})".format(
                    self.root, threads, ops, cond
                )
            )

        targets = [self.core.get(t) for t in self.depset]

        self.__generate_rdepends_lists(targets)
        works = licant.util.queue()

        class info_cls:
            def __init__(self):
                self.have_done = 0
                self.need_done = len(targets)
                self.sum = 0
                self.err = False

        info = info_cls()

        for t in targets:
            if t.rcounter == len(t.deps):
                works.put(t)

        lock = threading.Lock()

        def thread_func(index):
            while info.have_done != info.need_done:
                if info.err:
                    break

                lock.acquire()
                if not works.empty():
                    w = works.get()
                    lock.release()

                    if core.runtime["trace"]:
                        print("TRACE: THREAD {0} get work {1}".format(index, w))

                    if cond(w):
                        try:
                            ret = w.invoke(ops)
                        except:
                            info.err = True
                            return
                        if ret is False:
                            info.err = True
                            return
                        if ret == 0:
                            info.sum += 1

                    for r in [self.core.get(t) for t in w.rdepends]:
                        r.rcounter = r.rcounter + 1
                        if r.rcounter == len(r.deps):
                            works.put(r)

                    info.have_done += 1

                    if core.runtime["trace"]:
                        print(
                            "TRACE: THREAD {0} finished with work {1}".format(index, w)
                        )

                    continue
                lock.release()

        threads_list = [
            threading.Thread(target=thread_func, args=(i,)) for i in range(0, threads)
        ]

        for t in threads_list:
            t.start()

        for t in threads_list:
            t.join()

        if info.err:
            print(licant.util.red("runtime error (multithreads mode)"))
            exit(-1)
        return info.sum

    def reverse_recurse_invoke(self, *args, **kwargs):
        if "threads" in kwargs:
            if kwargs["threads"] == 1:
                return self.reverse_recurse_invoke_single(*args, **kwargs)
            else:
                return self.reverse_recurse_invoke_threads(*args, **kwargs)
        else:
            return self.reverse_recurse_invoke_single(*args, **kwargs)

    def __str__(self):
        ret = ""
        for d in sorted(self.depset):
            t = self.core.get(d)
            s = "{}: {}\n".format(d, sorted(t.deps))
            ret += s
        ret = ret[:-1]
        return ret


class Target:
    __actions__ = {"actlist"}

    def __init__(self, tgt, deps, actions=None, __help__=None, **kwargs):
        self.tgt = tgt
        self.deps = set(deps)
        for k, v in kwargs.items():
            setattr(self, k, v)

        if actions is not None:
            self.__actions__ = self.__actions__.union(set(actions))

        self.__help__ = __help__

    def get_deplist(self):
        return [self.core.get(d) for d in self.deps]

    def actlist(self):
        print(licant.util.get_actions(self))

    def hasaction(self, act):
        return act in self.__actions__

    def invoke(self, funcname, *args, critical=False, **kwargs):
        """Invoke func function or method, or mthod with func name for this target

		Поддерживается несколько разных типов func.
		В качестве func может быть вызвана внешняя функция с параметром текущей цели,
		или название локального метода.
		critical -- Действует для строкового вызова. Если данный attr отсутствует у цели,
		то в зависимости от данного параметра может быть возвращен None или выброшено исключение.
		"""
        if core.runtime["trace"]:
            print(
                "TRACE: Invoke: tgt:{}, act:{}, args:{}, kwargs:{}".format(
                    self.tgt, funcname, args, kwargs
                )
            )

        # if funcname not in self.__actions__:
        # 	licant.error("Isn't action {}".format(licant.util.yellow(funcname)))

        func = getattr(self, funcname, None)
        if func is None:
            if critical:
                raise WrongAction(func)
            return None

        if isinstance(func, types.MethodType):
            # return licant.util.cutinvoke(func, *args, **kwargs)
            return func(*args, **kwargs)

        else:
            # return licant.util.cutinvoke(func, self, *args, **kwargs)
            return func(self, *args, **kwargs)

    def __repr__(self):
        """По умолчанию вывод Target на печать возвращает идентификатор цели"""
        return self.tgt


class UpdateStatus(Enum):
    Waiting = 0
    Keeped = 1
    Updated = 2


class UpdatableTarget(Target):
    __actions__ = Target.__actions__.union(
        {"recurse_update", "update", "update_if_need"}
    )

    def __init__(
        self,
        tgt,
        deps,
        default_action="recurse_update",
        update_status=UpdateStatus.Waiting,
        **kwargs
    ):
        Target.__init__(self, tgt, deps, default_action=default_action, **kwargs)
        self.update_status = update_status

    def update(self):
        licant.error("Unoverrided update method")

    def self_need(self):
        return False

    def has_updated_depends(self):
        depends = self.get_deplist()

        for d in depends:
            if (
                not isinstance(d, UpdatableTarget)
                or d.update_status == UpdateStatus.Updated
            ):
                return True

            if d.update_status == UpdateStatus.Waiting:
                print(d)
                licant.error("Unwalked depends in UpdatableTarget")

        return False

    def update_if_need(self):
        if self.has_updated_depends() or self.self_need():  # self.invoke("self_need"):
            self.update_status = UpdateStatus.Updated
            return self.update()  # self.invoke("update")
        else:
            self.update_status = UpdateStatus.Keeped
            return True

    def recurse_update(self):
        stree = self.core.subtree(self.tgt)
        stree.reverse_recurse_invoke(
            ops="update_if_need", threads=core.runtime["threads"]
        )


class Routine(UpdatableTarget):
    __actions__ = {"recurse_update", "update", "actlist"}

    def __init__(self, func, deps=[], tgt=None, **kwargs):
        if tgt is None:
            tgt = func.__name__
        UpdatableTarget.__init__(self, tgt=tgt, deps=deps, **kwargs)
        self.func = func
        self.args = []

    def update(self):
        return self.func(*self.args)

    def self_need(self):
        return True

    def recurse_update(self, *args):
        self.args = args
        super().recurse_update()


def routine_decorator(func=None, deps=None):
    if inspect.isfunction(func):
        core.add(Routine(func))
        return func

    else:

        def decorator(func):
            core.add(Routine(func, deps=deps))
            return func

        return decorator


def print_targets_list(target, *args):
    if core.runtime["debug"]:
        print("print_targets_list args:{}".format(args))

    if len(core.targets) == 0:
        print("targets doesn't founded")
        return

    keys = sorted(core.targets.keys())

    if len(args) > 0:
        keys = [m for m in keys if re.search(args[0], m)]

    for k in keys:
        v = core.targets[k]
        print(k)


def print_target_info(taget, *args):
    if len(args) == 0:
        licant.error("Need target mnemo")

    print("name:", core.get(args[0]))
    print("deps:", sorted(core.get(args[0]).deps))


def print_deps(taget, *args):
    if len(args) == 0:
        name = licant.cli.default_target
    else:
        name = args[0]

    lst = sorted(core.depends_as_set(name))
    for l in lst:
        print(l)


def print_subtree(target, tgt):
    print(core.subtree(tgt))


corediag_target = Target(
    tgt="corediag",
    deps=[],
    targets=print_targets_list,
    tgtinfo=print_target_info,
    subtree=print_subtree,
    printdeps=print_deps,
    actions={"targets", "tgtinfo", "subtree", "printdeps"},
    __help__="Core state info",
)

core.add(corediag_target)


def do(lst):
    core.get(lst[0]).invoke(lst[1], *lst[2:])


def get_target(name):
    return core.get(name)
