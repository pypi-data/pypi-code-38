# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from ftw.recipe.solr.defaults import DEFAULT_OPTIONS
from ftw.recipe.solr.utils import chmod_executable
from jinja2 import Environment, PackageLoader
from setuptools import archive_util
from shutil import copyfile
from zc.buildout.download import Download
from zc.recipe.egg import Eggs
import os
import pkg_resources


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        for k, v in DEFAULT_OPTIONS.items():
            options.setdefault(k, v)

        options.setdefault('destination', os.path.join(
            buildout['buildout']['parts-directory'], self.name))

        options.setdefault('home-dir', os.path.join(
            buildout['buildout']['directory'], 'var', self.name))

        options.setdefault('log-dir', os.path.join(
            buildout['buildout']['directory'], 'var', 'log'))

        options.setdefault('bin-dir', os.path.join(
            buildout['buildout']['directory'], 'bin'))

        self.cores = options.get('cores', '').split()

        options.setdefault('pid-file', os.path.join(options['home-dir'],
                           '{}.pid'.format(name)))

        self.env = Environment(
            loader=PackageLoader('ftw.recipe.solr', 'templates'),
            trim_blocks=True,
        )

    def download_and_extract(self, url, md5sum, dest, extract_filter='*', strip_dirs=1):
        path, is_temp = Download(self.buildout['buildout'])(url, md5sum)
        files = []

        def progress_filter(src, dst):
            if fnmatch(src, extract_filter):
                stripped = os.path.normpath(src).split(os.sep)[strip_dirs:]
                if stripped:
                    files.append(os.path.join(dest, os.path.join(
                        *stripped)))
                    return files[-1]

        archive_util.unpack_archive(path, dest, progress_filter)
        return files

    def install(self):
        parts = []

        destination = self._create_dir(self.options.get('destination'), parts)

        # Download and extract Solr distribution
        parts.extend(self.download_and_extract(
            self.options['url'],
            self.options['md5sum'],
            destination,
        ))

        # Create Solr data directories
        home_dir = self._create_dir(self.options.get('home-dir'))
        log_dir = self._create_dir(self.options.get('log-dir'))

        # Create solr.xml
        parts.append(self._create_from_template(
            'solr.xml.tmpl',
            os.path.join(home_dir, 'solr.xml'),
        ))

        # Create zoo.cfg
        parts.append(self._create_from_template(
            'zoo.cfg.tmpl',
            os.path.join(home_dir, 'zoo.cfg'),
        ))

        # Determine the location of the egg containing the Solr conf files
        conf_egg = self.options.get('conf-egg')
        if conf_egg:
            eggs = Eggs(self.buildout, conf_egg, {})
            requirements, ws = eggs.working_set()
            requirement = pkg_resources.Requirement.parse(conf_egg)
            package = ws.find(requirement)
            conf_src_base_path = package.location
        else:
            conf_src_base_path = ''

        # Create cores
        for core in self.cores:
            core_dir = os.path.join(home_dir, core)
            if not os.path.isdir(core_dir):
                os.makedirs(core_dir)

            self._create_from_template(
                'core.properties.tmpl',
                os.path.join(core_dir, 'core.properties'),
                name=core,
            )

            core_conf_dir = os.path.join(core_dir, 'conf')
            if not os.path.isdir(core_conf_dir):
                os.makedirs(core_conf_dir)

            conf_src = self._core_option(core, 'conf')
            if not conf_src:
                conf_src = os.path.join(os.path.dirname(__file__), 'conf')
            if conf_src_base_path:
                conf_src = os.path.join(
                    conf_src_base_path, conf_src.lstrip('/'))
            parts.extend(
                self._copy_from_dir(conf_src, core_conf_dir)
            )

        # Create log4j2.xml
        log4j2_xml = os.path.join(destination, 'log4j2.xml')
        parts.append(self._create_from_template(
            'log4j2.xml.tmpl',
            log4j2_xml,
            logfile=os.path.join(log_dir, self.name + '.log'),
            slow_logfile=os.path.join(
                log_dir, self.name + '_slow_requests.log'),
        ))

        # Create startup script
        bin_dir = self.options['bin-dir']
        startup_script = os.path.join(bin_dir, self.name)
        parts.append(self._create_from_template(
            'startup.tmpl',
            startup_script,
            pid_file=self.options['pid-file'],
            jvm_opts=self.options['jvm-opts'],
            solr_port=self.options['port'],
            solr_host=self.options['host'],
            solr_home=home_dir,
            solr_install_dir=destination,
            log_dir=log_dir,
            log4j2_xml=log4j2_xml,
        ))
        chmod_executable(startup_script)

        return parts

    def update(self):
        return self.install()

    def _core_option(self, core, option, default=None):
        """Retrieve an option for a core from a subpart falling back to the
           main part."""
        core_part_name = "{}_{}".format(self.name, core)
        if core_part_name in self.buildout:
            if option in self.buildout[core_part_name]:
                return self.buildout[core_part_name][option]
        return self.options.get(option, default)

    def _create_dir(self, path, parts=None):
        if not os.path.isdir(path):
            os.makedirs(path)
            if parts:
                parts.append(path)
        return path

    def _create_from_template(self, template, filename, **kwargs):
        tmpl = self.env.get_template(template)
        with open(filename, 'wb') as f:
            f.write(tmpl.render(**kwargs).encode('utf8'))
        return filename

    def _copy_from_dir(self, src, dst):
        paths = []
        for name in os.listdir(src):
            dst_path = os.path.join(dst, name)
            copyfile(os.path.join(src, name),  dst_path)
            paths.append(dst_path)
        return paths
