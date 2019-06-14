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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import copy
import os
import shutil
import tempfile
import jinja2
import koji
import munch
import time
import random
import string
from productmd.composeinfo import ComposeInfo

import odcs.server.utils
from odcs.server import conf, log, db
from odcs.server import comps
from odcs.common.types import (
    PungiSourceType, COMPOSE_RESULTS, MULTILIB_METHODS,
    INVERSE_PUNGI_SOURCE_TYPE_NAMES, COMPOSE_FLAGS)
from odcs.server.utils import makedirs, clone_repo, copytree


class BasePungiConfig(object):

    def _write(self, path, cfg):
        """
        Writes configuration string `cfg` to file defined by `path`.

        :param str path: Full path to file to write to.
        :param str cfg: Configuration to write.
        """
        with open(path, "w") as f:
            log.info("Writing %s configuration to %s.",
                     os.path.basename(path), path)
            f.write(cfg)

    def write_config_files(self, topdir):
        """Write configuration into files"""
        raise NotImplementedError('Concrete config object must implement.')


class RawPungiConfig(BasePungiConfig):

    def __init__(self, compose_source):
        source_name, source_hash = compose_source.split("#")

        url_data = copy.deepcopy(conf.raw_config_urls[source_name])
        # Do not override commit hash by hash from ODCS client if it is
        # hardcoded in the config file.
        if "commit" not in url_data:
            url_data["commit"] = source_hash

        self.pungi_cfg = url_data
        self.pungi_koji_args = conf.raw_config_pungi_koji_args.get(
            source_name, conf.pungi_koji_args)

    def write_config_files(self, topdir):
        """Write raw config files

        :param str topdir: Directory to write the files to.
        """
        # In case the raw_config wrapper config is set, download the
        # original pungi.conf as "raw_config.conf" and use
        # the raw_config wrapper as real "pungi.conf".
        # The reason is that wrapper config can import raw_config
        # and override some variables.
        if conf.raw_config_wrapper_conf_path:
            main_cfg_path = os.path.join(topdir, "raw_config.conf")
            shutil.copy2(conf.raw_config_wrapper_conf_path,
                         os.path.join(topdir, "pungi.conf"))
        else:
            main_cfg_path = os.path.join(topdir, "pungi.conf")

        # Clone the git repo with raw_config pungi config files.
        repo_dir = os.path.join(topdir, "raw_config_repo")
        clone_repo(self.pungi_cfg["url"], repo_dir,
                   commit=self.pungi_cfg["commit"])

        # If the 'path' is defined, copy only the files form the 'path'
        # to topdir.
        if "path" in self.pungi_cfg:
            repo_dir = os.path.join(repo_dir, self.pungi_cfg["path"])

        copytree(repo_dir, topdir)

        # Create the "pungi.conf" from config_filename.
        config_path = os.path.join(topdir, self.pungi_cfg["config_filename"])
        if config_path != main_cfg_path:
            shutil.copy2(config_path, main_cfg_path)


class PungiConfig(BasePungiConfig):
    def __init__(self, release_name, release_version, source_type, source,
                 packages=None, arches=None, sigkeys=None, results=0,
                 multilib_arches=None, multilib_method=0, builds=None,
                 flags=0, lookaside_repos=None, modular_koji_tags=None,
                 module_defaults_url=None):
        self.release_name = release_name
        self.release_version = release_version
        self.bootable = False
        self.sigkeys = sigkeys.split(" ") if sigkeys else []
        self.source_type = source_type
        self.source = source
        self.koji_profile = conf.koji_profile
        self.pkgset_koji_inherit = True
        self.lookaside_repos = lookaside_repos.split(" ") if lookaside_repos else []
        self.include_devel_modules = []
        if arches:
            self.arches = arches
        else:
            self.arches = conf.arches
        self.packages = packages or []
        self.builds = builds or []

        # Store results as list of strings, so it can be used by jinja2
        # templates.
        self.results = []
        for k, v in COMPOSE_RESULTS.items():
            if results & v:
                self.results.append(k)

        self.multilib_arches = multilib_arches if multilib_arches else []
        self.multilib_method = []
        if multilib_method:
            for k, v in MULTILIB_METHODS.items():
                if multilib_method & v:
                    self.multilib_method.append(k)

        if "boot.iso" in self.results:
            self.bootable = True

        if source_type == PungiSourceType.KOJI_TAG:
            self.koji_module_tags = modular_koji_tags.split(" ") if modular_koji_tags else []
            self.module_defaults_url = module_defaults_url.split(" ") if module_defaults_url else []
            self.koji_tag = source
            self.gather_source = "comps"
            if self.koji_module_tags:
                self.gather_method = "hybrid"
            else:
                self.gather_method = "deps"
        elif source_type == PungiSourceType.MODULE:
            self.koji_tag = None
            self.gather_source = "module"
            self.gather_method = "nodeps"

            self._sort_out_devel_modules()

            if self.packages:
                raise ValueError("Exact packages cannot be set for MODULE "
                                 "source type.")
        elif source_type in [PungiSourceType.BUILD,
                             PungiSourceType.PUNGI_COMPOSE,
                             PungiSourceType.REPO]:
            self.gather_source = "comps"
            self.gather_method = "deps"
            self.koji_tag = None
        else:
            raise ValueError("Unknown source_type %r" % source_type)

        self.check_deps = bool(flags & COMPOSE_FLAGS["check_deps"])

    def _sort_out_devel_modules(self):
        """
        Helper method filtering out "-devel" modules from `self.source`
        and adding them to `include_devel_modules` list.
        """
        source_list = self.source.split(" ")
        new_source = []
        for nsvc in source_list:
            n, s, v, c = nsvc.split(":")

            # It does not have -devel suffix, so it is not -devel module.
            if not n.endswith("-devel"):
                new_source.append(nsvc)
                continue

            # If it is -devel module, there must exist the non-devel
            # counterpart.
            non_devel_nsvc = ":".join([n[:-len("-devel")], s, v, c])
            if non_devel_nsvc not in source_list:
                new_source.append(nsvc)
                continue

            self.include_devel_modules.append(":".join([n, s]))
        self.source = " ".join(new_source)

    @property
    def source_type_str(self):
        return INVERSE_PUNGI_SOURCE_TYPE_NAMES[self.source_type]

    @property
    def release_short(self):
        return self.release_name[:16]

    @property
    def comps_file(self):
        if self.source_type == PungiSourceType.MODULE:
            return None
        else:
            return "comps.xml"

    @property
    def pkgset_source(self):
        if self.source_type == PungiSourceType.REPO:
            return 'repos'
        return 'koji'

    def get_comps_config(self):
        if self.source_type == PungiSourceType.MODULE:
            return ""
        odcs_comps = comps.Comps()
        odcs_group = comps.Group('odcs-group', 'odcs-group', 'ODCS compose default group')
        for package in self.packages:
            odcs_group.add_package(comps.Package(package))
        odcs_comps.add_group(odcs_group)

        template = jinja2.Template(comps.COMPS_TEMPLATE)
        return template.render(comps=odcs_comps)

    def get_variants_config(self):
        odcs_product = comps.Product()
        tmp_variant = comps.Variant('Temporary', 'Temporary', 'variant', self.source_type)
        for arch in self.arches:
            tmp_variant.add_arch(comps.Arch(arch))
        if self.source_type == PungiSourceType.MODULE:
            for module in self.source.split(" "):
                tmp_variant.add_module(comps.Module(module))
        elif self.source_type == PungiSourceType.KOJI_TAG:
            if self.packages:
                tmp_variant.add_group(comps.Group('odcs-group', 'odcs-group', 'ODCS compose default group'))
            if self.koji_module_tags:
                tmp_variant.add_module(comps.Module("*"))

        odcs_product.add_variant(tmp_variant)

        template = jinja2.Template(comps.VARIANTS_TEMPLATE)
        return template.render(product=odcs_product)

    def get_pungi_config(self):
        try:
            with open(conf.pungi_conf_path) as fd:
                template = jinja2.Template(fd.read())
            return template.render(config=self)
        except Exception as e:
            log.exception(
                "Failed to render pungi conf template {!r}: {}".format(conf.pungi_conf_path,
                                                                       str(e)))

    def write_config_files(self, topdir):
        """
        Writes "pungi.conf", "variants.xml" and "comps.xml" defined in
        `self.pungi_cfg` to `topdir` directory.

        :param str topdir: Directory to write the files to.
        """
        main_cfg = self.get_pungi_config()
        variants_cfg = self.get_variants_config()
        comps_cfg = self.get_comps_config()
        log.debug("Main Pungi config:")
        log.debug("%s", main_cfg)
        log.debug("Variants.xml:")
        log.debug("%s", variants_cfg)
        log.debug("Comps.xml:")
        log.debug("%s", comps_cfg)

        self._write(os.path.join(topdir, "pungi.conf"), main_cfg)
        self._write(os.path.join(topdir, "variants.xml"), variants_cfg)
        self._write(os.path.join(topdir, "comps.xml"), comps_cfg)


class Pungi(object):
    def __init__(self, compose_id, pungi_cfg, koji_event=None, old_compose=None):
        self.compose_id = compose_id
        self.pungi_cfg = pungi_cfg
        self.koji_event = koji_event
        self.old_compose = old_compose

    def _write_cfgs(self, topdir):
        """Wrtie pungi config

        :param str topdir: Directory to write the files to.
        """
        self.pungi_cfg.write_config_files(topdir)
        if conf.pungi_runroot_koji_conf_path:
            shutil.copy2(conf.pungi_runroot_koji_conf_path,
                         os.path.join(topdir, "odcs_koji.conf"))

    def make_koji_session(self):
        """
        Creates new KojiSession according to odcs.server.conf, logins to
        Koji using this session and returns it.
        :rtype: koji.KojiSession
        :return: KojiSession
        """
        koji_config = munch.Munch(koji.read_config(
            profile_name=conf.koji_profile,
            user_config=conf.koji_config,
        ))

        address = koji_config.server
        authtype = koji_config.authtype
        log.info("Connecting to koji %r with %r." % (address, authtype))
        koji_session = koji.ClientSession(address, opts=koji_config)
        if authtype == "kerberos":
            ccache = getattr(conf, "koji_krb_ccache", None)
            keytab = getattr(conf, "koji_krb_keytab", None)
            principal = getattr(conf, "koji_krb_principal", None)
            log.debug("  ccache: %r, keytab: %r, principal: %r" % (
                ccache, keytab, principal))
            if keytab and principal:
                koji_session.krb_login(
                    principal=principal,
                    keytab=keytab,
                    ccache=ccache,
                )
            else:
                koji_session.krb_login(ccache=ccache)
        elif authtype == "ssl":
            koji_session.ssl_login(
                os.path.expanduser(koji_config.cert),
                None,
                os.path.expanduser(koji_config.serverca),
            )
        else:
            raise ValueError("Unrecognized koji authtype %r" % authtype)

        return koji_session

    def get_pungi_cmd(self, conf_topdir, targetdir, compose_dir=None):
        """
        Returns list with pungi command line arguments needed to generate
        the compose.
        :param str conf_topdir: Directory in which to look for Pungi
            configuration files.
        :param str targetdir: Target directory in which the compose should be
            generated.
        :param str compose_dir: If defined, overrides the Pungi compose_dir.
        :rtype: list
        :return: List of pungi command line arguments.
        """
        pungi_cmd = [
            conf.pungi_koji,
            "--config=%s" % os.path.join(conf_topdir, "pungi.conf"),
        ]

        if compose_dir:
            pungi_cmd.append("--compose-dir=%s" % compose_dir)
        else:
            pungi_cmd.append("--target-dir=%s" % targetdir)

        if isinstance(self.pungi_cfg, RawPungiConfig):
            pungi_cmd += self.pungi_cfg.pungi_koji_args
        elif isinstance(self.pungi_cfg, PungiConfig):
            pungi_cmd += conf.pungi_koji_args
        else:
            raise RuntimeError('Unknown pungi config type to handle.')

        if self.koji_event:
            pungi_cmd += ["--koji-event", str(self.koji_event)]
        if self.old_compose:
            pungi_cmd += ["--old-composes", self.old_compose]
        return pungi_cmd

    def _prepare_compose_dir(self, conf_topdir, targetdir):
        """
        Creates the compose directory and returns the full path to it.
        """
        compose_date = time.strftime("%Y%m%d", time.localtime())
        compose_id = "odcs-%s-1-%s.n.0" % (
            self.compose_id, compose_date)
        compose_dir = os.path.join(targetdir, compose_id)
        makedirs(compose_dir)

        # Generate ComposeInfo which is needed for Pungi.
        # These variables can be hardcoded, because we only generate composes
        # like this in ODCS.
        ci = ComposeInfo()
        ci.release.name = "odcs-%s" % self.compose_id
        ci.release.short = "odcs-%s" % self.compose_id
        ci.release.version = "1"
        ci.release.is_layered = False
        ci.release.type = "ga"
        ci.release.internal = False
        ci.compose.id = compose_id
        ci.compose.label = None
        ci.compose.type = "nightly"
        ci.compose.date = compose_date
        ci.compose.respin = 0

        # Dump the compose info to work/global/composeinfo-base.json.
        work_dir = os.path.join(compose_dir, "work", "global")
        makedirs(work_dir)
        ci.dump(os.path.join(work_dir, "composeinfo-base.json"))

        return compose_dir

    def run_locally(self):
        """
        Runs local Pungi compose.
        """
        td = None
        try:
            td = tempfile.mkdtemp()
            self._write_cfgs(td)
            compose_dir = self._prepare_compose_dir(td, conf.target_dir)
            pungi_cmd = self.get_pungi_cmd(td, conf.target_dir, compose_dir)

            log_out_path = os.path.join(compose_dir, "pungi-stdout.log")
            log_err_path = os.path.join(compose_dir, "pungi-stderr.log")

            with open(log_out_path, "w") as log_out:
                with open(log_err_path, "w") as log_err:
                    odcs.server.utils.execute_cmd(
                        pungi_cmd, cwd=td, timeout=conf.pungi_timeout,
                        stdout=log_out, stderr=log_err)
        finally:
            try:
                if td is not None:
                    shutil.rmtree(td)
            except Exception as e:
                log.warning(
                    "Failed to remove temporary directory {!r}: {}".format(
                        td, str(e)))

    def _unique_path(self, prefix):
        """
        Create a unique path fragment by appending a path component
        to prefix.  The path component will consist of a string of letter and numbers
        that is unlikely to be a duplicate, but is not guaranteed to be unique.
        """
        # Use time() in the dirname to provide a little more information when
        # browsing the filesystem.
        # For some reason repr(time.time()) includes 4 or 5
        # more digits of precision than str(time.time())
        # Unnamed Engineer: Guido v. R., I am disappoint
        return '%s/%r.%s' % (prefix, time.time(),
                             ''.join([random.choice(string.ascii_letters)
                                      for i in range(8)]))

    def upload_files_to_koji(self, koji_session, localdir):
        """
        Uploads files from `localdir` directory to Koji server using
        `koji_session`. The unique server-side directory containing
        the uploaded files is returned.
        :param koji.KojiSession koji_session: Koji session.
        "param str localdir: Path to directory with files to upload.
        """
        serverdir = self._unique_path("odcs")

        for name in sorted(os.listdir(localdir)):
            path = os.path.join(localdir, name)
            koji_session.uploadWrapper(path, serverdir, callback=None)

        return serverdir

    def run_in_runroot(self, compose):
        """
        Runs the compose in runroot, waits for a result and raises an
        exception if the Koji runroot tasks failed.
        """
        conf_topdir = os.path.join(conf.target_dir,
                                   self._unique_path("runroot_configs"))
        makedirs(conf_topdir)
        self._write_cfgs(conf_topdir)

        koji_session = self.make_koji_session()
        serverdir = self.upload_files_to_koji(koji_session, conf_topdir)

        cmd = []
        cmd += ["cp", "/mnt/koji/work/%s/*" % serverdir, ".", "&&"]
        cmd += ["cp", "./odcs_koji.conf", "/etc/koji.conf.d/", "&&"]
        cmd += self.get_pungi_cmd("./", conf.pungi_runroot_target_dir)

        kwargs = {
            'channel': conf.pungi_parent_runroot_channel,
            'packages': conf.pungi_parent_runroot_packages,
            'mounts': conf.pungi_parent_runroot_mounts,
            'weight': conf.pungi_parent_runroot_weight
        }

        task_id = koji_session.runroot(
            conf.pungi_parent_runroot_tag, conf.pungi_parent_runroot_arch,
            " ".join(cmd), **kwargs)

        compose.koji_task_id = task_id
        db.session.commit()

        while True:
            # wait for the task to finish
            if koji_session.taskFinished(task_id):
                break
            log.info("Waiting for Koji runroot task %r to finish...", task_id)
            time.sleep(60)

        info = koji_session.getTaskInfo(task_id)
        if info is None:
            raise RuntimeError("Cannot get status of Koji task %r" % task_id)
        state = koji.TASK_STATES[info['state']]
        if state in ('FAILED', 'CANCELED'):
            raise RuntimeError("Koji runroot task %r failed." % task_id)

    def run(self, compose):
        """
        Runs the compose in Pungi. Blocks until the compose is done.
        Raises an exception if compose generation fails.

        :param models.Compose compose: Compose this Pungi process is running
            for.
        """
        if conf.pungi_runroot_enabled:
            self.run_in_runroot(compose)
        else:
            self.run_locally()


class PungiLogs(object):
    def __init__(self, compose):
        self.compose = compose

    @property
    def global_log_path(self):
        """
        Returns the path to pungi.global.log if it exists.
        """
        toplevel_work_dir = self.compose.toplevel_work_dir
        if not toplevel_work_dir:
            return None
        return os.path.join(
            toplevel_work_dir, "logs", "global", "pungi.global.log")

    def _get_global_log_errors(self):
        """
        Helper method which opens the `self.global_log_path` and search for
        all errors in that log file.

        :rtype: list
        :return: List of error strings.
        """
        errors = []
        global_log_path = self.global_log_path
        if not global_log_path:
            return errors
        try:
            with open(global_log_path, "r") as global_log:
                error = ""
                for line in global_log.readlines():
                    idx = line.find("[ERROR   ]")
                    if idx == -1:
                        if error:
                            error += line
                            errors.append(error)
                            error = ""
                        continue
                    if error:
                        errors.append(error)
                    error = line[idx + len("[ERROR   ] "):]
        except IOError:
            pass
        return errors

    def get_error_string(self):
        """
        Returns the string with errors parsed from Pungi logs.

        :rtype: str
        :return: String with errors parsed from Pungi logs.
        """
        errors = ""

        global_errors = self._get_global_log_errors()
        for error in global_errors:
            if error.startswith("Extended traceback in:"):
                continue
            errors += error

        errors = errors.replace(
            conf.target_dir, conf.target_dir_url)
        return errors
