"""
Command: androidcreate
======================


--clean
-------


"""


from django.core.management.base import BaseCommand, CommandError
import os
import shutil

from ._tools import get_p4a_args, update_apk, parcefiles, overwrite_p4a, clean_build, read_configuration

#from radiant.core.toolchain import ToolchainCL
#from pythonforandroid.toolchain import ToolchainCL, Context, split_argument_list
from ._toolchain import RadiantToolchainCL#, load_bootstrap
#from pythonforandroid.toolchain import ToolchainCL


class Command(BaseCommand):
    help = 'Create a build for new project'
    can_import_settings = True

    #----------------------------------------------------------------------

    def add_arguments(self, parser):
        """"""

        parser.add_argument(
            '--clean',
            action='store_true',
            dest='clean',
            default=True,
            help='Delete all build components',
        )

    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        from django.conf import settings

        #load_bootstrap()
        update_apk(settings)

        build_dir = os.path.join(settings.ANDROID['BUILD']['build'], os.path.split(settings.BASE_DIR)[-1])
        #build_dir = os.path.join(settings.ANDROID['BUILD']['build'])
        os.chdir(build_dir)

        if options['clean']:
            clean_build(settings)

        argv = read_configuration(settings)

        #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        #os.system('p4a create {}'.format(argv))

        #argv.c['bootstrap'] = 'webview'

        tc = RadiantToolchainCL(argv)
        tc.create(argv)

        overwrite_p4a(settings)

