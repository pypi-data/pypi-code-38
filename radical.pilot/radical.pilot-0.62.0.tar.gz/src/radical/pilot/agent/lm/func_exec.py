

__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__   = "MIT"


from .base import LaunchMethod


# ==============================================================================
#
class FuncExec(LaunchMethod):

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg, session):

        LaunchMethod.__init__(self, cfg, session)


    # --------------------------------------------------------------------------
    #
    def _configure(self):

        self.launch_command = ''
        
        self._req = rpu_Pubsub(self._session, 'func_request', rpu_PUBSUB_PUB)
        self._res = rpu_Pubsub(self._session, 'func_result',  rpu_PUBSUB_SUB)

        self._res.subscribe('func_result')


    # --------------------------------------------------------------------------
    #
    @classmethod
    def lrms_config_hook(cls, name, cfg, lrms, logger, profiler):

        # FIXME: - start func_exec pubsub
        #        - start result    pubsub
        pass


    # --------------------------------------------------------------------------
    #
    def construct_command(self, cu, launch_script_hop):

        # NOTE: ignore thread and process counts, and expect application to do
        #       the needful

        slots        = cu['slots']
        cud          = cu['description']
        task_exec    = cud['executable']
        task_args    = cud.get('arguments') or []
        task_argstr  = self._create_arg_string(task_args)

        if task_argstr:
            command = "%s %s" % (task_exec, task_argstr)
        else:
            command = task_exec

        return command, None


# ------------------------------------------------------------------------------

