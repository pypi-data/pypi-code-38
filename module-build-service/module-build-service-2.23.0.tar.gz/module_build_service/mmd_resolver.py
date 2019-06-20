# -*- coding: utf-8 -*-
#
# Copyright © 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluža <jkaluza@redhat.com>
#            Igor Gnatenko <ignatenko@redhat.com>

import enum
import collections
import itertools
import solv
from module_build_service import log, conf
from module_build_service.models import ModuleBuild


class MMDResolverPolicy(enum.Enum):
    All = "all"  # All possible top-level combinations
    First = "first"  # All possible top-level combinations (filtered by N:S, first picked)


class MMDResolver(object):
    """
    Resolves dependencies between Module metadata objects.
    """

    def __init__(self):
        self.pool = solv.Pool()
        self.pool.setarch("x86_64")
        self.build_repo = self.pool.add_repo("build")
        self.available_repo = self.pool.add_repo("available")
        # Solvable objects representing modules stored in a list grouped by
        # the name:stream.
        self.solvables = {}

    def _deps2reqs(self, deps, base_module_stream_overrides=None, exact_versions=True):
        """
        Helper method converting dependencies from MMD to solv.Dep instance expressing
        the dependencies in a way libsolv accepts as input.

        So for example for following input:
            deps = [{'gtk': ['1'], 'foo': ['1']}]
        The resulting solv.Dep expression will be:
            ((module(gtk) with module(gtk:1)) and (module(foo) with module(foo:1)))

        Base modules are handled in a special way in case when the stream of base module
        contains version in the "x.y.z" format. For example "el8.0.0" or "el7.6.0".
        In this case, the resulting solv.Dep expression for such base module will contain version
        string computed using ModuleBuild.get_stream_version() method:
        For example:
            module(platform) with module(platform:el8) = 080200

        The stream used to compute the version can be also overridden using the
        `base_module_stream_overrides` dict which has base module name as a key and
        the stream which will be used to compute the version as a value.
        This is needed for cases when module requires just "platform:el8", but was
        in fact built against particular platform stream, for example platform:el8.1.0.
        In this case, such module should still require platform:el8, but in particular
        version which is passed to this method using the `base_module_stream_overrides`.

        When `exact_versions` is set to False, the base module dependency will contain
        ">=" operator instead of "=".

        The "with" syntax is here to allow depending on "module(gtk)" meaning "any gtk".
        This can happen in case {'gtk': []} is used as an input.

        See the inline comments for more information.

        :param list deps: List of dicts with dependency name as key and list of
            streams as value.
        :param dict base_module_stream_overrides: The key is base module name, value
            is the stream string which will be used to compute `version` part of the
            base module solv.Dep expression.
        :param bool exact_versions: When set to False, the base module dependency
            will contain ">=" operator instead of "=".
        :rtype: solv.Dep
        :return: solv.Dep instance with dependencies in form libsolv accepts.
        """
        pool = self.pool

        # Every name:stream combination from dict in `deps` list is expressed as `solv.Dep`
        # instance and is represented internally in solv with "module(name:stream)".
        # This is parallel to RPM-world "Provides: perl(foo)" or "Requires: perl(foo)",
        # but in this method, we are only constructing the condition after the "Provides:"
        # or "Requires:".
        # This method creates such solve.Dep.
        stream_dep = lambda n, s: pool.Dep("module(%s:%s)" % (n, s))
        versioned_stream_dep = lambda n, s, v, op: pool.Dep("module(%s:%s)" % (n, s)).Rel(
            op, pool.Dep(str(v))
        )

        # There are relations between modules in `deps`. For example:
        #   deps = [{'gtk': ['1'], 'foo': ['1']}]" means "gtk:1 and foo:1" are both required.
        #   deps = [{'gtk': ['1', '2']}"] means "gtk:1 or gtk:2" are required.
        # This method helps creating such relations using following syntax:
        #   rel_or_dep(solv.Dep, solve.REL_OR, stream_dep(name, stream))
        #   rel_or_dep(solv.Dep, solve.REL_AND, stream_dep(name, stream))
        #   rel_or_dep(solv.Dep, solve.REL_WITH, stream_dep(name, stream))
        #   rel_or_dep(solv.Dep, solve.REL_WITHOUT, stream_dep(name, stream))
        rel_or_dep = lambda dep, op, rel: dep.Rel(op, rel) if dep is not None else rel

        # Check each dependency dict in `deps` list and generate the solv requirements.
        reqs = None
        for dep_dicts in deps:
            # Contains the solv.Dep requirements for current dict.
            require = None
            for name, streams in dep_dicts.items():
                is_base_module = name in conf.base_module_names

                # The req_pos will store solv.Dep expression for "positive" requirements.
                # That is the case of 'gtk': ['1', '2'].
                # The req_neg will store negative requirements like 'gtk': ['-1', '-2'].
                req_pos = req_neg = None

                # For each stream in `streams` for this dependency, generate the
                # module(name:stream) solv.Dep and add REL_OR relations between them.
                for stream in streams:
                    if is_base_module:
                        # Override the stream which is used to compute the stream version in case
                        # `base_module_stream_overrides` is set.
                        if base_module_stream_overrides and name in base_module_stream_overrides:
                            stream_for_version = base_module_stream_overrides[name]
                        else:
                            stream_for_version = stream

                        # In case x.y.z versioning is not used for this base module, do not
                        # use versions solv.Dep.
                        stream_version_str = str(
                            ModuleBuild.get_stream_version(stream_for_version, right_pad=False))
                        if len(stream_version_str) < 5:
                            if stream.startswith("-"):
                                req_neg = rel_or_dep(
                                    req_neg, solv.REL_OR, stream_dep(name, stream[1:])
                                )
                            else:
                                req_pos = rel_or_dep(req_pos, solv.REL_OR, stream_dep(name, stream))
                        else:
                            # The main reason why to use `exact_versions` is the case when
                            # adding deps for the input module we want to resolve. This module
                            # buildrequires exact stream version of base module against which it
                            # needs for building and we should never pull in different one.
                            # But for modules which are buildrequires of this input module, we
                            # want to use "base_module >= stream_version" relation, because they
                            # can be chery-picked even when newer base module stream_version is
                            # requested, for example:
                            # - foo buildrequires bar and also buildrequires platform:el8 = 080100.
                            # - bar:1 is built against platform:el8.0.0.
                            # - bar:2 is built against platform:el8.2.0.
                            # We need libsolv to allow chery-picking "bar:1", and ignore "bar:2",
                            # because it is built against newer platform stream version than the
                            # requested and and such newer version can be incompatible with the
                            # old one. so we express bar's dependencies on platform like this:
                            # - bar:1 buildrequires platform:el8 >= 080000.
                            # - bar:2 buildrequires platform:el8 >= 080200.
                            # Because the "foo" limits the solving to platform:el8 = 080100,
                            # the bar:2 won't be returned by libsolv, because 080100 < 080200.
                            # But that bar:1 will be returned by libsovl, because it buildrequires
                            # platform 080000 which is lesser than 080100.
                            op = solv.REL_EQ
                            if not exact_versions:
                                op |= solv.REL_GT
                            version = ModuleBuild.get_stream_version(
                                stream_for_version, right_pad=False
                            )
                            if stream.startswith("-"):
                                req_neg = rel_or_dep(
                                    req_neg,
                                    solv.REL_OR,
                                    versioned_stream_dep(name, stream[1:], version, op),
                                )
                            else:
                                req_pos = rel_or_dep(
                                    req_pos,
                                    solv.REL_OR,
                                    versioned_stream_dep(name, stream, version, op),
                                )
                    else:
                        if stream.startswith("-"):
                            req_neg = rel_or_dep(req_neg, solv.REL_OR, stream_dep(name, stream[1:]))
                        else:
                            req_pos = rel_or_dep(req_pos, solv.REL_OR, stream_dep(name, stream))

                # Generate the module(name) solv.Dep.
                req = pool.Dep("module(%s)" % name)

                # Use the REL_WITH for positive requirements and REL_WITHOUT for negative
                # requirements.
                if req_pos is not None:
                    req = req.Rel(solv.REL_WITH, req_pos)
                elif req_neg is not None:
                    req = req.Rel(solv.REL_WITHOUT, req_neg)

                # And in the end use AND between the last name:[streams] and the current one.
                require = rel_or_dep(require, solv.REL_AND, req)

            # There might be multiple dicts in `deps` list, so use OR relation between them.
            reqs = rel_or_dep(reqs, solv.REL_OR, require)

        return reqs

    def _add_base_module_provides(self, solvable, mmd):
        """
        Adds the "stream version" and the "virtual_streams" from XMD section of `mmd` to `solvable`.

        Base modules like "platform" can contain virtual streams which need to be considered
        when resolving dependencies. For example module "platform:el8.1.0" can provide virtual
        stream "el8". In this case the solvable will have following additional Provides:

        - module(platform:el8.1.0) = 80100 - Modules can require specific platform stream.
        - module(platform:el8) = 80100 - Module can also require just platform:el8.
        """
        if mmd.get_module_name() not in conf.base_module_names:
            return

        # When depsolving, we will need to follow specific rules to choose the right base
        # module, like sorting the base modules sharing the same virtual streams based on
        # their "stream version" - For example stream "el8.1" is lower than stream "el8.2"
        # and so on. We therefore need to convert the stream and version of base module to
        # integer representation and add "module($name:$stream) = $stream_based_version"
        # to Provides.
        version = ModuleBuild.get_stream_version(mmd.get_stream_name(), right_pad=False)
        if version:
            dep = self.pool.Dep(
                "module(%s:%s)" % (mmd.get_module_name(), mmd.get_stream_name())
            ).Rel(
                solv.REL_EQ, self.pool.Dep(str(version))
            )
            solvable.add_deparray(solv.SOLVABLE_PROVIDES, dep)

        xmd = mmd.get_xmd()
        # Return in case virtual_streams are not set for this mmd.
        if not xmd.get("mbs", {}).get("virtual_streams"):
            return

        # For each virtual stream, add
        # "module($name:$stream) = $virtual_stream_based_version" provide.
        for stream in xmd["mbs"]["virtual_streams"]:
            dep = self.pool.Dep("module(%s:%s)" % (mmd.get_module_name(), stream)).Rel(
                solv.REL_EQ, self.pool.Dep(str(version)))
            solvable.add_deparray(solv.SOLVABLE_PROVIDES, dep)

    def _get_base_module_stream_overrides(self, mmd):
        """
        Checks the xmd["mbs"]["buildrequires"] and returns the dict containing
        base module name as a key and stream of base module against which this
        module was built. This is later used to override base module streams
        in the _deps2reqs method.

        :param Modulemd mmd: Metadata of module for which the stream overrides are returned.
        :rtype: dict
        :return: Dict with module name as a key and new stream as a value.
        """
        overrides = {}
        xmd = mmd.get_xmd()
        if "buildrequires" in xmd.get("mbs", {}):
            for base_module_name in conf.base_module_names:
                if base_module_name not in xmd["mbs"]["buildrequires"]:
                    continue
                if "stream" not in xmd["mbs"]["buildrequires"][base_module_name]:
                    continue
                stream = xmd["mbs"]["buildrequires"][base_module_name]["stream"]

                overrides[base_module_name] = stream
        return overrides

    def add_modules(self, mmd):
        """
        Adds module represented by `mmd` metadata to MMDResolver. Modules added by this
        method will be considered as possible dependencies while resolving the dependencies
        using the `solve(...)` method only if their "context" is None. Otherwise they are
        treated like input modules we want to resolve dependencies for.

        :param Modulemd mmd: Metadata of module to add.
        :rtype: list
        :return: list of solv.Solvable instances representing the module in libsolv world.
        """
        n, s, v, c = \
            mmd.get_module_name(), mmd.get_stream_name(), mmd.get_version(), mmd.get_context()
        pool = self.pool

        # Helper method to return the dependencies of `mmd` in the {name: [streams], ... form}.
        # The `dep_type` is either "runtime" or "buildtime" str depending on whether
        # the return deps should be runtime requires or buildrequires.
        normdeps = lambda mmd, dep_type: [
            {
                name: getattr(dep, "get_{}_streams".format(dep_type))(name)
                for name in getattr(dep, "get_{}_modules".format(dep_type))()
            }
            for dep in mmd.get_dependencies()
        ]

        base_module_stream_overrides = self._get_base_module_stream_overrides(mmd)

        # Each solvable object has name, version, architecture and list of
        # provides/requires/conflicts which defines its relations with other solvables.
        # You can imagine solvable as a single RPM.
        # Single module can be represented by multiple solvables - read further inline
        # comments for more info. Therefore we use list to store them.
        solvables = []
        if c is not None:
            # If context is set, the module we are adding should be used as dependencies
            # for input module. Therefore add it in "available_repo".
            solvable = self.available_repo.add_solvable()

            # Use n:s:v:c as name, version as version and set the arches.
            solvable.name = "%s:%s:%d:%s" % (n, s, v, c)
            solvable.evr = str(v)
            # TODO: replace with real arch, but for now resolving using single arch
            # is sufficient.
            solvable.arch = "x86_64"

            # Add "Provides: module(name)", each module provides itself.
            # This is used for example to find the buildrequired module when
            # no particular stream is used - for example when buildrequiring
            # "gtk: []"
            solvable.add_deparray(solv.SOLVABLE_PROVIDES, pool.Dep("module(%s)" % n))
            # Add "Provides: module(name:stream) = version", so we can find buildrequired
            # modules when "gtk:[1]" is used and also choose the latest version.
            solvable.add_deparray(
                solv.SOLVABLE_PROVIDES,
                pool.Dep("module(%s:%s)" % (n, s)).Rel(solv.REL_EQ, pool.Dep(str(v))),
            )

            self._add_base_module_provides(solvable, mmd)

            # Fill in the "Requires" of this module, so we can track its dependencies
            # on other modules.
            requires = self._deps2reqs(
                normdeps(mmd, "runtime"), base_module_stream_overrides, False
            )
            log.debug("Adding module %s with requires: %r", solvable.name, requires)
            solvable.add_deparray(solv.SOLVABLE_REQUIRES, requires)

            # Add "Conflicts: module(name)".
            # This is needed to prevent installation of multiple streams of single module.
            # For example:
            #  - "app:1" requires "foo:1" and "gtk:1".
            #  - "foo:1" requires "bar:1".
            #  - "gtk:1" requires "bar:2".
            # "bar:1" and "bar:2" cannot be installed in the same time and therefore
            # there need to be conflict defined between them.
            solvable.add_deparray(solv.SOLVABLE_CONFLICTS, pool.Dep("module(%s)" % n))
            solvables.append(solvable)

            # Add solvable to solvables list. Sorting is done later in the solve method.
            ns = ":".join([n, s])
            if ns not in self.solvables:
                self.solvables[ns] = []
            self.solvables[ns].append(solvable)
        else:
            # For input module, we might have multiple buildrequires/requires pairs in the
            # input `mmd`. For example like this:
            #   - buildrequires:
            #       gtk: [1]
            #       platform: [f28]
            #     requires:
            #       gtk: [1]
            #   - buildrequires:
            #       gtk: [2]
            #       platform: [f29]
            #     requires:
            #       gtk: [2]
            # This means we need: "(gtk:1 and platform:f28) or (gtk:2 and platform:f29)".
            # There is no way how to express that in libsolv as single solvable and in the same
            # time try all the possible combinations. Libsolv just returns the single one and does
            # not offer enough data for us to tell it to try another one to really find all of
            # them.
            # The solution for that is therefore adding multiple solvables for each OR block of
            # that input condition.
            #
            # So in our example, we add two solvables:
            #   1) Solvable with name "n:s:v:0" and "Requires: gtk:1 and platform:f28".
            #   2) Solvable with name "n:s:v:1" and "Requires: gtk:2 and platform:f29".
            #
            # Note the "context" field in the solvable name - it is set according to index
            # of buildrequires/requires pair and uniquely identifies the Solvable.
            #
            # Using this trick, libsolv will try to solve all the buildrequires/requires pairs,
            # because they are expressed as separate Solvables and we are able to distinguish
            # between them thanks to context value.
            normalized_deps = normdeps(mmd, "buildtime")
            for c, deps in enumerate(mmd.get_dependencies()):
                # $n:$s:$c-$v.src
                solvable = self.build_repo.add_solvable()
                solvable.name = "%s:%s:%d:%d" % (n, s, v, c)
                solvable.evr = str(v)
                solvable.arch = "src"

                requires = self._deps2reqs([normalized_deps[c]], base_module_stream_overrides)
                log.debug("Adding module %s with requires: %r", solvable.name, requires)
                solvable.add_deparray(solv.SOLVABLE_REQUIRES, requires)

                solvables.append(solvable)
                # Add solvable to solvables list. Sorting is done later in the solve method.
                ns = ":".join([n, s])
                if ns not in self.solvables:
                    self.solvables[ns] = []
                self.solvables[ns].append(solvable)

        return solvables

    def solve(self, mmd, policy=MMDResolverPolicy.First):
        """
        Solves dependencies of module defined by `mmd` object. Returns set
        containing frozensets with all the possible combinations which
        satisfied dependencies.

        :param Modulemd mmd: Input modulemd which should have the `context` set
            to None.
        :param policy: Policy to use when the dependencies used in buildrequires
            section are ambigous. For example, when the single buildrequired
            module is gtk:1 and this gtk:1 module is built against both
            platform:f28 and platform:f29, the policy influences the resolving
            in following way:

            - MMDResolverPolicy.First: Only single combination of buildrequires
              will be returned with "gtk:1" and "platform:f28", because the input
              buildrequires section did not mention any platform stream and
              therefore "first one" is used.
            - MMDResolverPolicy.All: Two combinations of buildrequires will be returned,
              one with "gtk:1" and "platform:f28", other with "gtk:1" and "platform:f29".

        :return: set of frozensets of n:s:v:c of modules which satisfied the
            dependency solving.
        """
        # Add the input module to pool and generate the "Provides" data so we can
        # use them for resolving later.
        solvables = self.add_modules(mmd)
        if not solvables:
            raise ValueError("No module(s) found for resolving")
        self.pool.createwhatprovides()

        # "solvable to n:s:v:c"
        s2nsvc = lambda s: "%s:%s" % (s.name, s.arch)
        # "solvable to n:s"
        s2ns = lambda s: ":".join(s.name.split(":", 2)[:2])

        # Sort the solvables by version for NSVC in descending order.
        for ns, unordered_solvables in self.solvables.items():
            unordered_solvables.sort(key=lambda s: int(s.name.split(":")[2]), reverse=True)

        # For each solvable object generated from input module, run the solver.
        # For reasons why there might be multiple solvable objects, please read the
        # `add_modules(...)` inline comments.
        solver = self.pool.Solver()
        alternatives = collections.OrderedDict()
        for src in solvables:
            # Create the solv Job to represent the solving task.
            job = self.pool.Job(solv.Job.SOLVER_INSTALL | solv.Job.SOLVER_SOLVABLE, src.id)

            # Check that at max 1 requires element exists in the solvable object - since
            # we create multiple solvable objects where each of them has at max one
            # requires element, it should never be the case...
            # NOTE: "requires" in solvable are actually "buildrequires" in mmd.
            requires = src.lookup_deparray(solv.SOLVABLE_REQUIRES)
            if len(requires) > 1:
                raise SystemError("At max one element should be in Requires: %s" % requires)
            elif len(requires) == 0:
                # Return early in case the requires is empty, because it basically means
                # the module has no buildrequires section.
                return set([frozenset([s2nsvc(src)])])

            requires = requires[0]
            src_alternatives = alternatives[src] = collections.OrderedDict()

            # TODO: replace this ugliest workaround ever with sane code of parsing rich deps.
            # We need to split them because whatprovides() treats "and" same way as "or" which is
            # not enough to generate combinations.
            # Source solvables have Req: (X and Y and Z)
            # Binary solvables have Req: ((X and Y) or (X and Z))
            # They do use "or" within "and", so simple string split won't work for binary packages.
            if src.arch != "src":
                raise NotImplementedError

            # What we get in `requires` here is a string in following format:
            #   ((module(gtk) with module(gtk:1)) and (module(foo) with module(foo:1)) and (...))
            # And what we want to get is the list of all valid combinations with particular NSVCs
            # of buildrequired modules. There are few steps we need to do to achieve that:

            # 1) Convert the "(R1 and R2 and R3)" string to list of solv.Dep in following format:
            #    [solv.Dep(R1), solv.Dep(R2), solv.Dep(R3), ...]
            deps = str(requires).split(" and ")
            if len(deps) > 1:
                # Remove the extra parenthesis in the input string in case there are more
                # rules.
                deps[0] = deps[0][1:]
                deps[-1] = deps[-1][:-1]
            # Generate the new deps using the parserpmrichdep.
            deps = [
                self.pool.parserpmrichdep(dep) if dep.startswith("(") else self.pool.Dep(dep)
                for dep in deps
            ]

            # 2) For each dep (name:stream), get the set of all solvables in particular NSVCs,
            #    which provides that name:stream. Then use itertools.product() to actually
            #    generate all the possible combinations so we can try solving them.
            for opt in itertools.product(*[self.pool.whatprovides(dep) for dep in deps]):
                log.debug("Testing %s with combination: %s", src, opt)
                # We will be trying to solve all the combinations using all the NSVCs
                # we have in pool, but as we said earlier, we don't want to return
                # all of them when MMDResolverPolicy.First is used.
                # We will achieve that by storing alternative combinations in `src_alternatives`
                # with NSVC as key in case we want all of them and NS as a key when we want
                # just First combination for given dependency.
                # This will allow us to group alternatives for single NS in case of First
                # policy and later return just the first alternative.
                if policy == MMDResolverPolicy.All:
                    kfunc = s2nsvc
                elif policy == MMDResolverPolicy.First:
                    kfunc = s2ns
                # `key` contains tuple similar to "('gtk:1', 'foo:1')"
                key = tuple(kfunc(s) for s in opt)

                # Create the solving jobs.
                # We need to say to libsolv that we want it to prefer modules from the combination
                # we are currently trying, otherwise it would just choose some random ones.
                # We do that by FAVORING those modules - this is done in libsolv by another
                # job prepending to our main job to resolve the deps of input module.
                jobs = [
                    self.pool.Job(solv.Job.SOLVER_FAVOR | solv.Job.SOLVER_SOLVABLE, s.id)
                    for s in opt
                ] + [job]

                # Log the job.
                log.debug("Jobs:")
                for j in jobs:
                    log.debug("  - %s", j)
                # Solve the deps and log the dependency issues.
                problems = solver.solve(jobs)
                if problems:
                    problem_str = self._detect_transitive_stream_collision(problems)
                    if problem_str:
                        err_msg = problem_str
                    else:
                        err_msg = ", ".join(str(p) for p in problems)
                    raise RuntimeError(
                        "Problems were found during module dependency resolution: {}".format(
                            err_msg)
                    )
                # Find out what was actually resolved by libsolv to be installed as a result
                # of our jobs - those are the modules we are looking for.
                newsolvables = solver.transaction().newsolvables()
                log.debug("Transaction:")

                for s in newsolvables:
                    log.debug("  - %s", s)

                # Skip this alternative in case not all the favored Solvables are in
                # the solution. For example if we favored gtk:4:1:c8, but it simply
                # cannot be installed because of other dependencies, we know this is not a
                # possible combination and we should not treat it as an alternative.
                all_solvables_found = True
                for s in opt:
                    if s not in newsolvables:
                        all_solvables_found = False
                        break

                # Append them as an alternative for this src_alternative.
                # Remember that src_alternatives are grouped by NS or NSVC depending on
                # MMDResolverPolicy, so there might be more of them.
                if all_solvables_found:
                    alternative = src_alternatives.setdefault(key, [])
                    alternative.append(newsolvables)
                else:
                    log.debug("  - ^ Not all favored solvables found in the result, skipping.")

        # If the MMDResolverPolicy is First, we will check all the alternatives and keep
        # just the "first" one.
        if policy == MMDResolverPolicy.First:
            # Prune
            for transactions in alternatives.values():
                for ns, trans in transactions.items():
                    # Each transaction in trans lists all the possible working
                    # combination of solvables. Our goal here is to find out the
                    # transaction which installs the most latest Solvables - ideally
                    # always the latest versions of the Solvables we have, but this might
                    # not be always possible because of dependencies.
                    #
                    # We achieve that by generating sorted_trans list in follwing format:
                    #   [[transaction_id, [solvable1_index, solvable2_index, ...]], [...], ...]
                    #
                    # The solvableN_index is a number saying how new the solvable is. We use
                    # `self.solvables` to get that number and it is simply index
                    # of the solvable in the particular self.solvables[name_stream] list.
                    # The newest solvable has therefore index 0, the next newest solvable index 1
                    # and so on.
                    #
                    # Then we simply sort the `sorted_trans` based on the sum of solvableN_index
                    # which gives us the transaction with the most recent versions. This is
                    # used as a solution.
                    sorted_trans = []
                    for i, t in enumerate(trans):
                        idx = []
                        for s in t:
                            name_stream = s2ns(s)
                            if name_stream not in self.solvables:
                                continue
                            index = self.solvables[name_stream].index(s)
                            idx.append(index)
                        sorted_trans.append([i, idx])
                    sorted_trans.sort(key=lambda i: sum(i[1]))
                    if sorted_trans:
                        transactions[ns] = [trans[sorted_trans[0][0]]]

        # Convert the solvables in alternatives to nsvc and return them as set of frozensets.
        return set(
            frozenset(s2nsvc(s) for s in transactions[0])
            for src_alternatives in alternatives.values()
            for transactions in src_alternatives.values()
        )

    @staticmethod
    def _detect_transitive_stream_collision(problems):
        """Return problem description if transitive stream collision happens

        Transitive stream collision could happen if different buildrequired
        modules requires same module but with different streams. For example,

        app:1 --br--> gtk:1 --req--> baz:1* -------- req --------> platform:f29
             |                                                     ^
             +--br--> foo:1 --req--> bar:1 --req--> baz:2* --req---|

        as a result, ``baz:1`` will conflicts with ``baz:2``.

        :param problems: list of problems returned from ``solv.Solver.solve``.
        :return: a string of problem description if transitive stream collision
            is detected. The description is provided by libsolv without
            changed. If no such collision, None is returned.
        :rtype: str or None
        """

        def find_conflicts_pairs():
            for problem in problems:
                for rule in problem.findallproblemrules():
                    info = rule.info()
                    if info.type == solv.Solver.SOLVER_RULE_PKG_CONFLICTS:
                        pair = [info.solvable.name, info.othersolvable.name]
                        pair.sort()  # only for pretty print
                        yield pair

        formatted_conflicts_pairs = ", ".join(
            "{} and {}".format(*item) for item in find_conflicts_pairs()
        )
        if formatted_conflicts_pairs:
            return "The module has conflicting buildrequires of: {}".format(
                formatted_conflicts_pairs)
