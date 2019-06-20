# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
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
# Written by Stanislav Ochotnicky <sochotnicky@redhat.com>
#            Jan Kaluza <jkaluza@redhat.com>

import calendar
import hashlib
import logging
import json
import os
import pkg_resources
import platform
import shutil
import subprocess
import tempfile
import time
from io import open
from itertools import chain

import kobo.rpmlib

from six import text_type
import koji
import pungi.arch

from module_build_service import conf, log, build_logs, Modulemd
from module_build_service.scm import SCM
from module_build_service.utils import to_text_type, load_mmd, mmd_to_str

logging.basicConfig(level=logging.DEBUG)


def get_session(config, login=True):
    from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder

    return KojiModuleBuilder.get_session(config, login=login)


def strip_suffixes(s, suffixes):
    """
    Helper function to remove suffixes from given string.

    At most, a single suffix is removed to avoid removing portions
    of the string that were not originally at its end.

    :param str s: String to operate on
    :param iter<str> tokens: Iterable of suffix strings
    :rtype: str
    :return: String without any of the given suffixes
    """
    for suffix in suffixes:
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s


def koji_retrying_multicall_map(*args, **kwargs):
    """
    Wrapper around KojiModuleBuilder.koji_retrying_multicall_map, because
    we cannot import that method normally because of import loop.
    """
    from module_build_service.builder.KojiModuleBuilder import (
        koji_retrying_multicall_map as multicall,)

    return multicall(*args, **kwargs)


class KojiContentGenerator(object):
    """ Class for handling content generator imports of module builds into Koji """

    def __init__(self, module, config):
        """
        :param module: module_build_service.models.ModuleBuild instance.
        :param config: module_build_service.config.Config instance
        """
        self.owner = module.owner
        self.module = module
        self.module_name = module.name
        self.mmd = to_text_type(module.modulemd)
        self.config = config
        self.devel = False
        # List of architectures the module is built for.
        self.arches = []
        # List of RPMs tagged in module.koji_tag as returned by Koji.
        self.rpms = []
        # Dict constructed from `self.rpms` with NEVRA as a key.
        self.rpms_dict = {}

    def __repr__(self):
        return "<KojiContentGenerator module: %s>" % (self.module_name)

    @staticmethod
    def parse_rpm_output(output, tags, separator=";"):
        """
        Copied from:
        https://github.com/projectatomic/atomic-reactor/blob/master/atomic_reactor/plugins/exit_koji_promote.py
        License: BSD 3-clause

        Parse output of the rpm query.
        :param output: list, decoded output (str) from the rpm subprocess
        :param tags: list, str fields used for query output
        :return: list, dicts describing each rpm package
        """  # noqa: E501

        def field(tag):
            """
            Get a field value by name
            """
            try:
                value = fields[tags.index(tag)]
            except ValueError:
                return None

            if value == "(none)":
                return None

            return value

        components = []
        sigmarker = "Key ID "
        for rpm in output:
            fields = rpm.rstrip("\n").split(separator)
            if len(fields) < len(tags):
                continue

            signature = field("SIGPGP:pgpsig") or field("SIGGPG:pgpsig")
            if signature:
                parts = signature.split(sigmarker, 1)
                if len(parts) > 1:
                    signature = parts[1]

            component_rpm = {
                u"type": u"rpm",
                u"name": field("NAME"),
                u"version": field("VERSION"),
                u"release": field("RELEASE"),
                u"arch": field("ARCH"),
                u"sigmd5": field("SIGMD5"),
                u"signature": signature,
            }

            # Special handling for epoch as it must be an integer or None
            epoch = field("EPOCH")
            if epoch is not None:
                epoch = int(epoch)

            component_rpm[u"epoch"] = epoch

            if component_rpm["name"] != "gpg-pubkey":
                components.append(component_rpm)

        return components

    def __get_rpms(self):
        """
        Copied from https://github.com/projectatomic/atomic-reactor/blob/master/atomic_reactor/plugins/exit_koji_promote.py
        License: BSD 3-clause

        Build a list of installed RPMs in the format required for the
        metadata.
        """  # noqa

        tags = [
            "NAME",
            "VERSION",
            "RELEASE",
            "ARCH",
            "EPOCH",
            "SIGMD5",
            "SIGPGP:pgpsig",
            "SIGGPG:pgpsig",
        ]

        sep = ";"
        fmt = sep.join(["%%{%s}" % tag for tag in tags])
        cmd = "/bin/rpm -qa --qf '{0}\n'".format(fmt)
        with open("/dev/null", "r+") as devnull:
            p = subprocess.Popen(
                cmd, shell=True, stdin=devnull, stdout=subprocess.PIPE, stderr=devnull)

            (stdout, stderr) = p.communicate()
            status = p.wait()
            output = stdout.decode("utf-8")

        if status != 0:
            log.debug("%s: stderr output: %s", cmd, stderr)
            raise RuntimeError("%s: exit code %s" % (cmd, status))

        return self.parse_rpm_output(output.splitlines(), tags, separator=sep)

    def __get_tools(self):
        """Return list of tools which are important for reproducing mbs outputs"""

        return [{"name": "libmodulemd", "version": Modulemd.get_version()}]

    def _koji_rpms_in_tag(self, tag):
        """ Return the list of koji rpms in a tag. """
        log.debug("Listing rpms in koji tag %s", tag)
        session = get_session(self.config, login=False)

        try:
            rpms, builds = session.listTaggedRPMS(tag, latest=True)
        except koji.GenericError:
            log.exception("Failed to list rpms in tag %r", tag)
            # If the tag doesn't exist.. then there are no rpms in that tag.
            return []

        # Module does not contain any RPM, so return an empty list.
        if not rpms:
            return []

        # Get the exclusivearch, excludearch and license data for each RPM.
        # The exclusivearch and excludearch lists are set in source RPM from which the RPM
        # was built.
        # Create temporary dict with source RPMs in rpm_id:rpms_list_index format.
        src_rpms = {}
        binary_rpms = {}
        for rpm in rpms:
            if rpm["arch"] == "src":
                src_rpms[rpm["id"]] = rpm
            else:
                binary_rpms[rpm["id"]] = rpm
        # Prepare the arguments for Koji multicall.
        # We will call session.getRPMHeaders(...) for each SRC RPM to get exclusivearch,
        # excludearch and license headers.
        multicall_kwargs = [
            {"rpmID": rpm_id, "headers": ["exclusivearch", "excludearch", "license"]}
            for rpm_id in src_rpms.keys()
        ]
        # For each binary RPM, we only care about the "license" header.
        multicall_kwargs += [
            {"rpmID": rpm_id, "headers": ["license"]} for rpm_id in binary_rpms.keys()
        ]
        rpms_headers = koji_retrying_multicall_map(
            session, session.getRPMHeaders, list_of_kwargs=multicall_kwargs
        )

        # Temporary dict with build_id as a key to find builds easily.
        builds = {build["build_id"]: build for build in builds}

        # Create a mapping of build IDs to SRPM NEVRAs so that the for loop below can directly
        # access these values when adding the `srpm_nevra` key to the returned RPMs
        build_id_to_srpm_nevra = {
            srpm["build_id"]: kobo.rpmlib.make_nvra(srpm, force_epoch=True)
            for srpm in src_rpms.values()
        }
        # Handle the multicall result. For each build associated with the source RPM,
        # store the exclusivearch and excludearch lists. For each RPM, store the 'license' and
        # also other useful data from the Build associated with the RPM.
        for rpm, headers in zip(chain(src_rpms.values(), binary_rpms.values()), rpms_headers):
            if not headers:
                raise RuntimeError("No RPM headers received from Koji for RPM %s" % rpm["name"])
            if "license" not in headers:
                raise RuntimeError(
                    "No RPM 'license' header received from Koji for RPM %s" % rpm["name"])
            build = builds[rpm["build_id"]]
            if "exclusivearch" in headers and "excludearch" in headers:
                build["exclusivearch"] = headers["exclusivearch"]
                build["excludearch"] = headers["excludearch"]

            rpm["license"] = headers["license"]
            rpm["srpm_name"] = build["name"]
            rpm["srpm_nevra"] = build_id_to_srpm_nevra[rpm["build_id"]]
            rpm["exclusivearch"] = build["exclusivearch"]
            rpm["excludearch"] = build["excludearch"]

        return rpms

    def _get_build(self):
        ret = self.module.nvr
        if self.devel:
            ret["name"] += "-devel"
        ret[u"source"] = self.module.scmurl
        ret[u"start_time"] = calendar.timegm(self.module.time_submitted.utctimetuple())
        ret[u"end_time"] = calendar.timegm(self.module.time_completed.utctimetuple())
        ret[u"extra"] = {
            u"typeinfo": {
                u"module": {
                    u"module_build_service_id": self.module.id,
                    u"content_koji_tag": self.module.koji_tag,
                    u"modulemd_str": self.module.modulemd,
                    u"name": ret["name"],
                    u"stream": self.module.stream,
                    u"version": self.module.version,
                    u"context": self.module.context,
                }
            }
        }
        session = get_session(self.config, login=False)
        # Only add the CG build owner if the user exists in Koji
        if session.getUser(self.owner):
            ret[u"owner"] = self.owner
        return ret

    def _get_buildroot(self):
        version = pkg_resources.get_distribution("module-build-service").version
        distro = platform.linux_distribution()
        ret = {
            u"id": 1,
            u"host": {
                u"arch": text_type(platform.machine()),
                u"os": u"%s %s" % (distro[0], distro[1]),
            },
            u"content_generator": {
                u"name": u"module-build-service",
                u"version": text_type(version),
            },
            u"container": {u"arch": text_type(platform.machine()), u"type": u"none"},
            u"components": self.__get_rpms(),
            u"tools": self.__get_tools(),
        }
        return ret

    def _koji_rpm_to_component_record(self, rpm):
        """
        Helper method returning CG "output" for RPM from the `rpm` dict.

        :param dict rpm: RPM dict as returned by Koji.
        :rtype: dict
        :return: CG "output" dict.
        """
        return {
            u"name": rpm["name"],
            u"version": rpm["version"],
            u"release": rpm["release"],
            u"arch": rpm["arch"],
            u"epoch": rpm["epoch"],
            u"sigmd5": rpm["payloadhash"],
            u"type": u"rpm",
        }

    def _get_arch_mmd_output(self, output_path, arch):
        """
        Returns the CG "output" dict for architecture specific modulemd file.

        :param str output_path: Path where the modulemd files are stored.
        :param str arch: Architecture for which to generate the "output" dict.
        :param dict rpms_dict: Dictionary with all RPMs built in this module.
            The key is NEVRA string, value is RPM dict as obtained from Koji.
            This dict is used to generate architecture specific "components"
            section in the "output" record.
        :rtype: dict
        :return: Dictionary with record in "output" list.
        """
        ret = {
            "buildroot_id": 1,
            "arch": arch,
            "type": "file",
            "extra": {"typeinfo": {"module": {}}},
            "checksum_type": "md5",
        }

        # Noarch architecture represents "generic" modulemd.txt.
        if arch == "noarch":
            mmd_filename = "modulemd.txt"
        else:
            mmd_filename = "modulemd.%s.txt" % arch

        # Read the modulemd file to get the filesize/checksum and also
        # parse it to get the Modulemd instance.
        mmd_path = os.path.join(output_path, mmd_filename)
        try:
            with open(mmd_path, "rb") as mmd_f:
                raw_data = mmd_f.read()
                data = to_text_type(raw_data)
                mmd = load_mmd(data)
                ret["filename"] = mmd_filename
                ret["filesize"] = len(raw_data)
                ret["checksum"] = hashlib.md5(raw_data).hexdigest()
        except IOError:
            if arch == "src":
                # This might happen in case the Module is submitted directly
                # using the yaml without SCM URL. This should never happen
                # when building production-ready modules using Koji, but in
                # theory it is possible.
                log.warning("No modulemd.src.txt found.")
                return
            else:
                raise

        components = []
        if arch in ["noarch", "src"]:
            # For generic noarch/src modulemd, include all the RPMs.
            for rpm in self.rpms:
                components.append(self._koji_rpm_to_component_record(rpm))
        else:
            # Check the RPM artifacts built for this architecture in modulemd file,
            # find the matching RPM in the `rpms_dict` coming from Koji and use it
            # to generate list of components for this architecture.
            # We cannot simply use the data from MMD here without `rpms_dict`, because
            # RPM sigmd5 signature is not stored in MMD.
            for rpm in mmd.get_rpm_artifacts():
                if rpm not in self.rpms_dict:
                    raise RuntimeError(
                        "RPM %s found in the final modulemd but not in Koji tag." % rpm)
                tag_rpm = self.rpms_dict[rpm]
                components.append(self._koji_rpm_to_component_record(tag_rpm))
        ret["components"] = components
        return ret

    def _get_output(self, output_path):
        ret = []
        for arch in self.arches + ["noarch", "src"]:
            mmd_dict = self._get_arch_mmd_output(output_path, arch)
            if mmd_dict:
                ret.append(mmd_dict)

        try:
            log_path = os.path.join(output_path, "build.log")
            with open(log_path, "rb") as build_log:
                checksum = hashlib.md5(build_log.read()).hexdigest()
            stat = os.stat(log_path)
            ret.append(
                {
                    u"buildroot_id": 1,
                    u"arch": u"noarch",
                    u"type": u"log",
                    u"filename": u"build.log",
                    u"filesize": stat.st_size,
                    u"checksum_type": u"md5",
                    u"checksum": checksum,
                }
            )
        except IOError:
            # no log file?
            log.error("No module build log file found. Excluding from import")

        return ret

    def _get_content_generator_metadata(self, output_path):
        ret = {
            u"metadata_version": 0,
            u"buildroots": [self._get_buildroot()],
            u"build": self._get_build(),
            u"output": self._get_output(output_path),
        }

        return ret

    def _should_include_rpm(self, rpm, mmd, arch, multilib_arches):
        """
        Helper method for `_fill_in_rpms_list` returning True if the RPM object
        should be included in a final MMD file for given arch.
        """
        # Check the "whitelist" buildopts section of MMD.
        # When "whitelist" is defined, it overrides component names from
        # `mmd.get_rpm_component(component)`. The whitelist is used when module needs to build
        # package with different SRPM name than the package name. This is case for example
        # for software collections where SRPM name can be "httpd24-httpd", but package name
        # is still "httpd". In this case, the component would contain "httpd", but the
        # rpm["srpm_name"] would be "httpd24-httpd".
        srpm = rpm["srpm_name"]
        whitelist = None
        buildopts = mmd.get_buildopts()
        if buildopts:
            whitelist = buildopts.get_rpm_whitelist()
            if whitelist:
                if srpm not in whitelist:
                    # Package is not in the whitelist, skip it.
                    return False

        # If there is no whitelist, just check that the SRPM name we have here
        # exists in the list of components.
        # In theory, there should never be situation where modular tag contains
        # some RPM built from SRPM not included in get_rpm_component_names() or in whitelist,
        # but the original Pungi code checked for this case.
        if not whitelist and srpm not in mmd.get_rpm_component_names():
            return False

        # Do not include this RPM if it is filtered.
        if rpm["name"] in mmd.get_rpm_filters():
            return False

        # Skip the rpm if it's built for multilib arch, but
        # multilib is not enabled for this srpm in MMD.
        try:
            mmd_component = mmd.get_rpm_component(srpm)
            multilib = set(mmd_component.get_multilib_arches())
            # The `multilib` set defines the list of architectures for which
            # the multilib is enabled.
            #
            # Filter out RPMs from multilib architectures if multilib is not
            # enabled for current arch. Keep the RPMs from non-multilib compatible
            # architectures.
            if arch not in multilib and rpm["arch"] in multilib_arches:
                return False
        except AttributeError:
            # TODO: This exception is raised only when "whitelist" is used.
            # Since components in whitelist have different names than ones in
            # components list, we won't find them there.
            # We would need to track the RPMs srpm_name from whitelist back to
            # original package name used in MMD's components list. This is possible
            # but original Pungi code is not doing that. This is TODO for future
            # improvements.

            # No such component, disable any multilib
            if rpm["arch"] not in ("noarch", arch):
                return False
        return True

    def _fill_in_rpms_list(self, mmd, arch):
        """
        Fills in the list of built RPMs in architecture specific `mmd` for `arch`
        using the data from `self.rpms_dict` as well as the content licenses field.

        :param Modulemd.ModuleStream mmd: MMD to add built RPMs to.
        :param str arch: Architecture for which to add RPMs.
        :rtype: Modulemd.Module
        :return: MMD with built RPMs filled in.
        """
        # List of all architectures compatible with input architecture including
        # the multilib architectures.
        # Example input/output:
        #   "x86_64" -> ['x86_64', 'athlon', 'i686', 'i586', 'i486', 'i386', 'noarch']
        #   "i686" -> ['i686', 'i586', 'i486', 'i386', 'noarch']
        compatible_arches = pungi.arch.get_compatible_arches(arch, multilib=True)
        # List of only multilib architectures.
        # For example:
        #   "x86_64" -> ['athlon', 'i386', 'i586', 'i486', 'i686']
        #   "i686" -> []
        multilib_arches = set(compatible_arches) - set(pungi.arch.get_compatible_arches(arch))
        # List of architectures that should be in ExclusiveArch tag or missing
        # from ExcludeArch tag. Multilib should not be enabled here.
        exclusive_arches = pungi.arch.get_valid_arches(arch, multilib=False, add_noarch=False)

        # A set into which we will add the RPMs.
        rpm_artifacts = set()

        # A set into which we will add licenses of all RPMs.
        rpm_licenses = set()

        # RPM name suffixes for debug RPMs.
        debug_suffixes = ("-debuginfo", "-debugsource")

        # The Name:NEVRA of source RPMs which are included in final MMD.
        non_devel_source_rpms = {}

        # Map source RPM name to NEVRA.
        source_rpms = {}

        # Names of binary RPMs in the Koji tag.
        binary_rpm_names = set()

        # Names of binary RPMs for which the `self._should_include()` method returned True.
        included_rpm_names = set()

        # Names source RPMs which have some RPM built from this SRPM included in a final MMD.
        included_srpm_names = set()

        # We need to evaluate the non-debug RPMs at first to find out which are included
        # in the final MMD and then decide whether to include the debug RPMs based on that.
        # In order to do that, we need to group debug RPMs and non-debug RPMs.
        # We also fill in the `binary_rpm_names` and `source_rpms` here.
        debug_rpms = {}
        non_debug_rpms = {}
        for nevra, rpm in self.rpms_dict.items():
            if rpm["arch"] == "src":
                source_rpms[rpm["name"]] = nevra
            else:
                binary_rpm_names.add(rpm["name"])
            if rpm["name"].endswith(debug_suffixes):
                debug_rpms[nevra] = rpm
            else:
                non_debug_rpms[nevra] = rpm

        # Check each RPM in Koji tag to find out if it can be included in mmd
        # for this architecture.
        for nevra, rpm in chain(non_debug_rpms.items(), debug_rpms.items()):
            # Filter out source RPMs, these will later be included if
            # the "main" RPM is included.
            if rpm["arch"] == "src":
                continue

            # Filter out RPMs which will never end up in final modulemd:
            # - the architecture of an RPM is not multilib architecture for `arch`.
            # - the architecture of an RPM is not the final mmd architecture.
            # - the architecture of an RPM is not "noarch" or "src".
            if rpm["arch"] not in multilib_arches and rpm["arch"] not in [arch, "noarch", "src"]:
                continue

            # Skip the RPM if it is excluded on this arch or exclusive
            # for different arch.
            if rpm["excludearch"] and set(rpm["excludearch"]) & set(exclusive_arches):
                continue
            if rpm["exclusivearch"] and not set(rpm["exclusivearch"]) & set(exclusive_arches):
                continue

            # The debug RPMs are handled differently ...
            if rpm["name"].endswith(debug_suffixes):
                # We include foo-debuginfo/foo-debugsource RPMs only in one of these cases:
                # - The "foo" is included in a MMD file (it means it is not filtered out).
                # - The "foo" package does not exist at all (it means only foo-debuginfo exists
                #   and we need to include this package unless filtered out) and in the same time
                #   the SRPM from which this -debuginfo/-debugsource RPM has been built is included
                #   in a final MMD (it means that there is at least some package from this build
                #   included - this handles case when only foo.src.rpm and foo-debugsource.rpm
                #   would be included in the final MMD, which would be wrong.)
                # We also respect filters here, so it is possible to explicitely filter out also
                # -debuginfo/-debugsource packages.
                main_rpm_name = strip_suffixes(rpm["name"], debug_suffixes)
                if (main_rpm_name in included_rpm_names or (
                        main_rpm_name not in binary_rpm_names
                        and rpm["srpm_name"] in included_srpm_names)):
                    should_include = self._should_include_rpm(rpm, mmd, arch, multilib_arches)
                else:
                    should_include = False
            else:
                should_include = self._should_include_rpm(rpm, mmd, arch, multilib_arches)

            # A source RPM should be included in a -devel module only if all the
            # RPMs built from this source RPM are included in a -devel module.
            # The list of source RPMs in non-devel module is tracked in
            # the `non_devel_source_rpms` dict and is later used to create complement
            # list for -devel modules.
            if should_include:
                non_devel_source_rpms[rpm["name"]] = rpm["srpm_nevra"]
                included_rpm_names.add(rpm["name"])
                included_srpm_names.add(rpm["srpm_name"])

            if self.devel and should_include:
                # In case this is a -devel module, we want to skip any RPMs which would normally be
                # included in a module, and only keep those which wouldn't be included, because
                # -devel is complementary to the normal module build.
                continue
            elif not self.devel and not should_include:
                # In case this is a normal (non-devel) module, include only packages which we
                # really should include and skip the others.
                continue

            rpm_artifacts.add(nevra)
            # Not all RPMs have licenses (for example debuginfo packages).
            license = rpm.get("license")
            if license:
                rpm_licenses.add(license)

        if self.devel:
            for source_nevra in set(source_rpms.values()) - set(non_devel_source_rpms.values()):
                rpm_artifacts.add(source_nevra)
        else:
            for source_nevra in non_devel_source_rpms.values():
                rpm_artifacts.add(source_nevra)

        # There is no way to replace the licenses, so remove any extra licenses
        for license_to_remove in (set(mmd.get_content_licenses()) - rpm_licenses):
            mmd.remove_content_license(license_to_remove)
        for license_to_add in (rpm_licenses - set(mmd.get_content_licenses())):
            mmd.add_content_license(license_to_add)

        # There is no way to replace the RPM artifacts, so remove any extra RPM artifacts
        for artifact_to_remove in (set(mmd.get_rpm_artifacts()) - rpm_artifacts):
            mmd.remove_rpm_artifact(artifact_to_remove)
        for artifact_to_add in (rpm_artifacts - set(mmd.get_rpm_artifacts())):
            mmd.add_rpm_artifact(artifact_to_add)
        return mmd

    def _sanitize_mmd(self, mmd):
        """
        Returns sanitized modulemd file.

        This method mainly removes the internal only information from the
        modulemd file which should not leak to final modulemd.

        :param Modulemd mmd: Modulemd instance to sanitize.
        :rtype: Modulemd.
        :return: Sanitized Modulemd instance.
        """
        # Remove components.repository and components.cache.
        for pkg_name in mmd.get_rpm_component_names():
            pkg = mmd.get_rpm_component(pkg_name)
            if pkg.get_repository():
                pkg.set_repository(None)
            if pkg.get_cache():
                pkg.set_cache(None)

        # Remove 'mbs' XMD section.
        xmd = mmd.get_xmd()
        if "mbs" in xmd:
            del xmd["mbs"]
            mmd.set_xmd(xmd)

        return mmd

    def _finalize_mmd(self, arch):
        """
        Finalizes the modulemd:
            - Fills in the list of built RPMs respecting filters, whitelist and multilib.

        :param str arch: Name of arch to generate the final modulemd for.
        :rtype: str
        :return: Finalized modulemd string.
        """
        mmd = self._sanitize_mmd(self.module.mmd())
        if self.devel:
            # Set the new name
            mmd = mmd.copy(mmd.get_module_name() + "-devel")

            # Depend on the actual module
            for dep in mmd.get_dependencies():
                dep.add_runtime_stream(mmd.get_module_name(), mmd.get_stream_name())

            # Delete API and profiles
            for rpm in mmd.get_rpm_api():
                mmd.remove_rpm_api(rpm)
            mmd.clear_profiles()

        # Set the "Arch" field in mmd.
        mmd.set_arch(pungi.arch.tree_arch_to_yum_arch(arch))
        # Fill in the list of built RPMs.
        mmd = self._fill_in_rpms_list(mmd, arch)

        return mmd_to_str(mmd)

    def _download_source_modulemd(self, mmd, output_path):
        """
        Fetches the original source modulemd file from SCM URL stored in the
        XMD section of `mmd` and stores it to filename referenced by `output_path`.

        This method does nothing if SCM URL is not set in the `mmd`.

        :param Modulemd mmd: Modulemd instance.
        :param str output_path: Full path to file into which the original modulemd
            file will be stored.
        """
        xmd = mmd.get_xmd()
        commit = xmd.get("mbs", {}).get("commit")
        scmurl = xmd.get("mbs", {}).get("scmurl")
        if not commit or not scmurl:
            log.warning("%r: xmd['mbs'] does not contain 'commit' or 'scmurl'.", self.module)
            return

        td = None
        try:
            log.info("Fetching %s (%s) to get the source modulemd.yaml", scmurl, commit)
            td = tempfile.mkdtemp()
            scm = SCM(scmurl)
            scm.commit = commit
            scm.checkout(td)
            fn = scm.get_module_yaml()
            log.info("Writing source modulemd.yaml to %r" % output_path)
            shutil.copy(fn, output_path)
        finally:
            try:
                if td is not None:
                    shutil.rmtree(td)
            except Exception as e:
                log.warning("Failed to remove temporary directory {!r}: {}".format(td, str(e)))

    def _prepare_file_directory(self):
        """ Creates a temporary directory that will contain all the files
        mentioned in the outputs section

        Returns path to the temporary directory
        """
        prepdir = tempfile.mkdtemp(prefix="koji-cg-import")
        mmd_path = os.path.join(prepdir, "modulemd.txt")
        log.info("Writing generic modulemd.yaml to %r" % mmd_path)
        with open(mmd_path, "w", encoding="utf-8") as mmd_f:
            mmd_f.write(self.mmd)

        mmd_path = os.path.join(prepdir, "modulemd.src.txt")
        self._download_source_modulemd(self.module.mmd(), mmd_path)

        for arch in self.arches:
            mmd_path = os.path.join(prepdir, "modulemd.%s.txt" % arch)
            log.info("Writing %s modulemd.yaml to %r" % (arch, mmd_path))
            mmd = self._finalize_mmd(arch)
            with open(mmd_path, "w", encoding="utf-8") as mmd_f:
                mmd_f.write(mmd)

        log_path = os.path.join(prepdir, "build.log")
        try:
            source = build_logs.path(self.module)
            log.info("Moving logs from %r to %r" % (source, log_path))
            shutil.copy(source, log_path)
        except IOError as e:
            log.exception(e)
        return prepdir

    def _upload_outputs(self, session, metadata, file_dir):
        """
        Uploads output files to Koji hub.
        """
        to_upload = []
        for info in metadata["output"]:
            if info.get("metadata_only", False):
                continue
            localpath = os.path.join(file_dir, info["filename"])
            if not os.path.exists(localpath):
                err = "Cannot upload %s to Koji. No such file." % localpath
                log.error(err)
                raise RuntimeError(err)

            to_upload.append([localpath, info])

        # Create unique server directory.
        serverdir = "mbs/%r.%d" % (time.time(), self.module.id)

        for localpath, info in to_upload:
            log.info("Uploading %s to Koji" % localpath)
            session.uploadWrapper(localpath, serverdir, callback=None)
            log.info("Upload of %s to Koji done" % localpath)

        return serverdir

    def _tag_cg_build(self):
        """
        Tags the Content Generator build to module.cg_build_koji_tag.
        """
        session = get_session(self.config)

        tag_name = self.module.cg_build_koji_tag
        if not tag_name:
            log.info(
                "%r: Not tagging Content Generator build, no cg_build_koji_tag set", self.module)
            return

        tag_names_to_try = [tag_name, self.config.koji_cg_default_build_tag]
        for tag in tag_names_to_try:
            log.info("Trying %s", tag)
            tag_info = session.getTag(tag)
            if tag_info:
                break

            log.info("%r: Tag %s not found in Koji, trying next one.", self.module, tag)

        if not tag_info:
            log.warning(
                "%r:, Not tagging Content Generator build, no available tag found, tried %r",
                self.module, tag_names_to_try,
            )
            return

        build = self._get_build()
        nvr = "%s-%s-%s" % (build["name"], build["version"], build["release"])

        log.info("Content generator build %s will be tagged as %s in Koji", nvr, tag)
        session.tagBuild(tag_info["id"], nvr)

    def _load_koji_tag(self, koji_session):
        # Do not load Koji tag data if this method is called again. This would
        # waste resources, because the Koji tag content is always the same
        # for already built module.
        if self.arches and self.rpms and self.rpms_dict:
            return

        tag = koji_session.getTag(self.module.koji_tag)
        self.arches = tag["arches"].split(" ") if tag["arches"] else []
        self.rpms = self._koji_rpms_in_tag(self.module.koji_tag)
        self.rpms_dict = {kobo.rpmlib.make_nvra(rpm, force_epoch=True): rpm for rpm in self.rpms}

    def koji_import(self, devel=False):
        """This method imports given module into the configured koji instance as
        a content generator based build

        Raises an exception when error is encountered during import

        :param bool devel: True if the "-devel" module should be created and imported.
            The "-devel" module build contains only the RPMs which are normally filtered
            from the module build. If set to False, normal module build respecting the
            filters is created and imported.
        """
        self.devel = devel
        session = get_session(self.config)
        self._load_koji_tag(session)

        file_dir = self._prepare_file_directory()
        metadata = self._get_content_generator_metadata(file_dir)
        try:
            serverdir = self._upload_outputs(session, metadata, file_dir)
            try:
                build_info = session.CGImport(metadata, serverdir)
            except koji.GenericError as e:
                if "Build already exists" not in str(e):
                    raise
                log.warning("Failed to import content generator")
                build_info = None
            if conf.koji_cg_tag_build:
                self._tag_cg_build()
            if build_info is not None:
                log.info("Content generator import done.")
                log.debug(json.dumps(build_info, sort_keys=True, indent=4))

                # Only remove the logs if CG import was successful.  If it fails,
                # then we want to keep them around for debugging.
                log.info("Removing %r", file_dir)
                shutil.rmtree(file_dir)
        except Exception as e:
            log.exception("Content generator import failed: %s", e)
            raise e
