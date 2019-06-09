from pythonforandroid.toolchain import ToolchainCL, Context, split_argument_list
from pythonforandroid.bootstrap import Bootstrap
import importlib
from pythonforandroid.logger import logger
from os.path import join


########################################################################
class RadiantToolchainCL(ToolchainCL):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, args):
        """Constructor"""

        self.args = args

        self.warn_on_deprecated_args(args)

        self.ctx = Context()
        self.storage_dir = args.storage_dir
        self.ctx.setup_dirs(self.storage_dir)
        self.sdk_dir = args.sdk_dir
        self.ndk_dir = args.ndk_dir
        self.android_api = args.android_api
        self.ndk_api = args.ndk_api
        self.ctx.symlink_java_src = args.symlink_java_src
        self.ctx.java_build_tool = args.java_build_tool

        self._archs = split_argument_list(args.arch)

        self.ctx.local_recipes = args.local_recipes
        self.ctx.copy_libs = args.copy_libs

        # Each subparser corresponds to a method
        #getattr(self, args.subparser_name.replace('-', '_'))(args)


#########################################################################
#class RadiantBootstrap:
    #""""""

    ##----------------------------------------------------------------------
    #@classmethod
    #def get_bootstrap(cls, name, ctx):
        #'''Returns an instance of a bootstrap with the given name.

        #This is the only way you should access a bootstrap class, as
        #it sets the bootstrap directory correctly.
        #'''

        ##name = 'django'

        #if name is None:
            #return None
        #if not hasattr(cls, 'bootstraps'):
            #cls.bootstraps = {}
        #if name in cls.bootstraps:
            #return cls.bootstraps[name]
        #mod = importlib.import_module('radiant.bootstraps.{}'
                                      #.format(name))
        #if len(logger.handlers) > 1:
            #logger.removeHandler(logger.handlers[1])
        #bootstrap = mod.bootstrap
        #bootstrap.bootstrap_dir = join(ctx.root_dir, 'bootstraps', name)
        #bootstrap.ctx = ctx
        #return bootstrap


##----------------------------------------------------------------------
#def load_bootstrap():
    #""""""

    #Bootstrap.get_bootstrap = RadiantBootstrap.get_bootstrap
