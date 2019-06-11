#


""" Core functionalities """


import distutils
import os
import subprocess
import tempfile
import venv
import zipapp

import setuptools


class _EnvBuilder(venv.EnvBuilder):

    def __init__(self, *args, **kwargs):
        self.context = None
        super().__init__(*args, **kwargs)

    def post_setup(self, context):
        """ Overrride """
        self.context = context


def _venv_create(venv_dir):
    venv_builder = _EnvBuilder(with_pip=True)
    venv_builder.create(venv_dir)
    venv_context = venv_builder.context
    return venv_context


def _install_to_dir(target_dir, requirements):
    """ Use pip to install the requirements into a specific directory
    """
    # pip is not usable as a library, so it is much simpler and safer to just
    # create a virtual environment and run a pip process from there
    with tempfile.TemporaryDirectory() as venv_dir:
        venv_context = _venv_create(venv_dir)
        command = [
            venv_context.env_exe,
            '-m', 'pip',
            'install',
            '--target', target_dir,
        ] + requirements
        subprocess.run(command)


def _create_zipapp_archive(source_dir, entry_point, output_file):
    zipapp.create_archive(
        source_dir,
        interpreter='/usr/bin/env python3',
        main=entry_point,
        target=output_file,
    )


def build_zapp(requirements, entry_point, output_file):
    """ Build a zapp binary archive
    """
    with tempfile.TemporaryDirectory() as install_dir:
        if requirements:
            _install_to_dir(install_dir, requirements)
        _create_zipapp_archive(install_dir, entry_point, output_file)


class bdist_zapp(setuptools.Command):  # pylint: disable=invalid-name
    """ Custom 'setuptools' command to build a zipapp
    """

    description = "create a zipapp archive"

    user_options = [
        (
            'entry-point=',
            'e',
            "entry point for the generated 'zipapp'",
        ),
        (
            'bdist-dir=',
            'b',
            "temporary directory for creating the distribution",
        ),
        (
            'dist-dir=',
            'd',
            "directory to put final built distributions in",
        ),
        (
            'keep-temp',
            'k',
            "keep the pseudo-installation tree around after creating the "
            "distribution archive",
        ),
    ]

    boolean_options = [
        'keep-temp',
    ]

    def __init__(self, *args, **kwargs):
        self.bdist_dir = None
        self.dist_dir = None
        self.entry_point = None
        self.keep_temp = 0
        super().__init__(*args, **kwargs)

    def initialize_options(self):
        """ Override """
        self.bdist_dir = None
        self.dist_dir = None
        self.entry_point = None

    def finalize_options(self):
        """ Override """
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'zapp')

        self.set_undefined_options(
            'bdist',
            (
                'dist_dir',
                'dist_dir',
            ),
        )

    def run(self):
        """ Override """
        if not self.entry_point:
            raise distutils.errors.DistutilsOptionError(
                "no entry point selected",
            )
        output_file = os.path.join(
            self.dist_dir,
            '{}-{}.pyz'.format(
                self.distribution.get_name(),
                self.distribution.get_version(),
            ),
        )
        distutils.log.info(
            "Building zipapp '{}' with entry point '{}'".format(
                output_file,
                self.entry_point,
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            dist_cmd = self.reinitialize_command('bdist_wheel')
            dist_cmd.bdist_dir = os.path.join(temp_dir, 'build')
            dist_cmd.dist_dir = os.path.join(temp_dir, 'dist')
            self.run_command('bdist_wheel')
            dist_file = None
            for dist in dist_cmd.distribution.dist_files:
                if dist[0] == 'bdist_wheel':
                    dist_file = dist[2]
            if not dist_file:
                raise distutils.errors.DistutilsInternalError(
                    "can not find bdist_wheel",
                )
            _install_to_dir(self.bdist_dir, [dist_file])
            self.mkpath(self.dist_dir)
            _create_zipapp_archive(
                self.bdist_dir,
                self.entry_point,
                output_file,
            )
            if not self.keep_temp:
                distutils.dir_util.remove_tree(
                    self.bdist_dir,
                    dry_run=self.dry_run,
                )


# EOF
