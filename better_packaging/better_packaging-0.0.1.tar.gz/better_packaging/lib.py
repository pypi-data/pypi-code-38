import codecs
import os
import subprocess
import sys

from importlib import import_module
from importlib.abc import MetaPathFinder

import better_exceptions
import pip
from pigar.__main__ import (
    Color,
    ReqsModules,
    check_latest_version,
    database,
    is_stdlib,
    lines_diff,
    project_import_modules,
)


class PipMetaPathFinder(MetaPathFinder):
    """
    A importlib.abc.MetaPathFinder to auto-install missing modules using pip
    """

    def find_spec(fullname, path, target=None):
        # print("fullname, path", fullname, path)
        # if path == None:
        #     installed = pip.main(["install", fullname])
        #     if installed == 0:
        #         return import_module(fullname)
        pass


# sys.meta_path.append(PipMetaPathFinder)


def hook(exc, value, tb):
    if not isinstance(value, ModuleNotFoundError):
        better_exceptions.excepthook(exc, value, tb)
        return
    print(Color.BLUE(f"better_packaging: {value}"))
    gr = GenerateReqs("pip.txt", os.getcwd(), [], [], "==")
    has_diff = gr.generate_reqs()
    if not has_diff:
        sys.__excepthook__(exc, value, tb)
        return
    subprocess.check_call("pip install -r pip.txt".split(), shell=False, timeout=None)
    python = sys.executable
    os.execl(python, python, *sys.argv)
    return


sys.excepthook = hook


class GenerateReqs(object):
    def __init__(
        self, save_path, project_path, ignores, installed_pkgs, comparison_operator="=="
    ):
        self._save_path = save_path
        self._project_path = project_path
        self._ignores = ignores
        self._installed_pkgs = installed_pkgs
        self._maybe_local_mods = set()
        self._comparison_operator = comparison_operator

    def generate_reqs(self):
        reqs, try_imports, guess = self.extract_reqs()
        in_pypi = set()
        pyver = None

        guess.remove(*try_imports)
        if guess:
            for name, detail in guess.sorted_items():
                with database() as db:
                    rows = db.query_all(name)
                    pkgs = [row.package for row in rows]
                    if pkgs:
                        in_pypi.add(name)
                        if name in self._maybe_local_mods:
                            self._maybe_local_mods.remove(name)
                    for pkg in self._best_matchs(name, pkgs):
                        latest = check_latest_version(pkg)
                        reqs.add(pkg, latest, detail.comments)

        # Save old requirements file.
        self._save_old_reqs()
        # Write requirements to file.
        self._write_reqs(reqs)
        del reqs
        guess.remove(*(in_pypi | self._maybe_local_mods))
        return self._reqs_diff()

    def extract_reqs(self):
        """Extract requirements from project."""
        reqs = ReqsModules()
        guess = ReqsModules()
        modules, try_imports, local_mods = project_import_modules(
            self._project_path, self._ignores
        )
        app_name = os.path.basename(self._project_path)
        if app_name in local_mods:
            local_mods.remove(app_name)

        # Filtering modules
        candidates = self._filter_modules(modules, local_mods)

        print("Check module in local environment.")
        for name in candidates:
            # print("Checking module: %s", name)
            if name in self._installed_pkgs:
                pkg_name, version = self._installed_pkgs[name]
                reqs.add(pkg_name, version, modules[name])
            else:
                guess.add(name, 0, modules[name])
        print("Finish local environment checking.")
        return reqs, try_imports, guess

    def _write_reqs(self, reqs):
        print(Color.BLUE('Writing requirements to "{0}"'.format(self._save_path)))
        with open(self._save_path, "w+") as f:

            for k, v in reqs.sorted_items():
                if k == "-e":
                    f.write("{0} {1}\n".format(k, v.version))
                elif v:
                    f.write(
                        "{0} {1} {2}\n".format(k, self._comparison_operator, v.version)
                    )
                else:
                    f.write("{0}\n".format(k))

    def _best_matchs(self, name, pkgs):
        # If imported name equals to package name.
        if name in pkgs:
            return [pkgs[pkgs.index(name)]]
        # If not, return all possible packages.
        return pkgs

    def _filter_modules(self, modules, local_mods):
        candidates = set()

        print("Filtering modules ...")
        for module in modules:
            # print("Checking module: %s", module)
            if not module or module.startswith("."):
                continue
            if module in local_mods:
                self._maybe_local_mods.add(module)
            if is_stdlib(module):
                continue
            candidates.add(module)

        return candidates

    def _invalid_reqs(self, reqs):
        pass

    def pip_file(self) -> [str]:
        with codecs.open(self._save_path, "r") as f:
            return f.readlines()

    def _save_old_reqs(self):
        if os.path.isfile(self._save_path):
            with codecs.open(self._save_path, "rb", "utf-8") as f:
                self._old_reqs = f.readlines()

    def _reqs_diff(self):
        if not hasattr(self, "_old_reqs"):
            return
        with codecs.open(self._save_path, "rb", "utf-8") as f:
            new_reqs = f.readlines()
        is_diff, diffs = lines_diff(self._old_reqs, new_reqs)
        msg = "Requirements file has been covered, "
        if is_diff:
            msg += "there is the difference:"
            print("{0}\n{1}".format(Color.YELLOW(msg), "".join(diffs)), end="")
        else:
            msg += "no difference."
            print(Color.YELLOW(msg))
        return is_diff
