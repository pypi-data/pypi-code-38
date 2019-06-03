#!/usr/bin/env python3
"""Script to extract a list of first-level dependencies using pip.

Warning: This file is not meant to be imported as a module.

Examples:
    $ python get_pip_deps.py pandas==0.24

        {
            "requirements": {
                "pytz": "pytz>=2011k",
                "numpy": "numpy>=1.12.0",
                "python-dateutil": "python-dateutil>=2.5.0"
            }
        }

    $ python get_pip_deps.py n0nex1st3nt

        {
            "error": "Not found."
        }
"""
import json
import os
import sys
import tempfile
import warnings
from io import StringIO
from typing import List

# Sin: Importing from protected modules
from pip._internal import main
from pip._internal.resolve import Resolver, ensure_dir
from pip._internal.req.req_install import InstallRequirement


def get_dependencies(r: str) -> List[InstallRequirement]:
    """Get direct dependencies for a requirement string.

    :param r: Requirement - it can be a package name or a name
       with version specification.

    It runs the equivalent of `pip download` command
    with a monkey-patched resolver that stops at the
    first level of dependency tree.

    This hack works, but keep this in mind:
        1) Monkey patching is a bad idea in general.
        2) Relying on anything starting with a "_" is a bad idea.
        3) Pip documentation explicitly discourages attempts to use it as library.

    The resolver is simplified a bit - we removed the parts
    that are not used.
    
    Examples:
        >>> get_dependencies("pandas==0.24")
        [<InstallRequirement object: numpy>=1.12.0 (from pandas==0.24) editable=False>,
         <InstallRequirement object: python-dateutil>=2.5.0 (from pandas==0.24) editable=False>,
         <InstallRequirement object: pytz>=2011k (from pandas==0.24) editable=False>]
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        found_reqs = []  # type: List[InstallRequirement]

        # Sin: Monkey-patching
        def new_resolve(self, requirement_set):
            # make the wheelhouse
            if self.preparer.wheel_download_dir:
                ensure_dir(self.preparer.wheel_download_dir)

            # If any top-level requirement has a hash specified, enter
            # hash-checking mode, which requires hashes from all.
            root_reqs = (
                requirement_set.unnamed_requirements +
                list(requirement_set.requirements.values())
            )
            self.require_hashes = (
                requirement_set.require_hashes or
                any(req.has_hash_options for req in root_reqs)
            )

            for req in root_reqs:
                found_reqs.extend(self._resolve_one(requirement_set, req))

        Resolver.resolve = new_resolve

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                main(["download", r, "-qqqqq"])
        except Exception:
            pass

        if "Could not find" in sys.stderr.getvalue():
            raise RuntimeError("Not found.")

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    found_reqs.sort(key=lambda l: l.name)
    return found_reqs


def run():
    """Get the dependencies and write them to stdout in JSON format.

    It takes the first argument from the command line.
    """
    req = sys.argv[1]
    try:
        deps = get_dependencies(req)
        data = {
            "requirements": {
                dep.name: str(dep.req) for dep in deps
            }
        }
    except RuntimeError as exc:
        data = {
            "error": str(exc)
        }
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    run()
else:
    warnings.warn("`get_pip_deps` is not meant to be imported as module.")
