
from .proxy import Proxy

class PtyProxy(Proxy):

    ''' 

    Different RCT layers need to frequently interact with shell environments on
    remote resources.  This `PtyProxy` class provides that functionality.  

    Thye class inherits from the `ru.Proxy` class, and accepts the same initial
    parameters which are then used to create a tunnel to the target resource.
    Once that tunnel is established, we'll bootstrap a small Python/ZMQ server
    endpoint on the target resource and connect to it.  That enspoint will be
    used to interface to the remote OS, by serving as a command execution
    service.

    The service endpoint is considered ephemeral, but it will keep some state on
    the target machine's disk space and thus can reconnect to that state.
    Commands which are executed by the service endpoint can survive the endpoint
    itself, and can also be revconnected to.  Any instance of the `PtyProcess`
    class will thus have access to the complete history of all previous
    instances targeting the same resource (the `purge()` method will clean out
    that history, and later incarnations may limit history by time or size).

    # FIXME: make this configurable

    The serive endpoint will create a Python virtualenv on the target resource
    on the fly (or reuse it when it exists).  The default location is in
    `$HOME/.radical/utils/ptyproxy/ve/`.

    # FIXME: make this configurable
    # FIXME: make resource details configurable (`module load python` etc.).
    #        Limit this to a bare minimum, ie. expect a POSIX shell and basic
    #        Python.

    The class also provides basic file transfer capablities.  Those should
    suffice to move scripts and coinfiguration files around, but are likely very
    inefficient for any larger and/or binary data transfer.
    ''' 

    # --------------------------------------------------------------------------
    #
    def __init__(self, url=None, timeout=None):

        super(Proxy, self).__init__(url=url, timeout=timeout)

        self._connected = False


    # --------------------------------------------------------------------------
    #
    def is_connected(self, _raise=False):

        if _raise and not self._connected:
            raise RuntimeError('not connected')
        
        return self._connected


    # --------------------------------------------------------------------------
    #
    def purge(self):

        self.is_connected(_raise=True)

        ret = self._run_command({'cmd' : 'purge'})
        if not ret.get('ret'):
            raise RuntimeError('purge failed: %s' % ret.get('error'))


    # --------------------------------------------------------------------------
    #
    def stage_to_remote(self, src, tgt=None):
        pass


    # --------------------------------------------------------------------------
    #
    def stage_from_remote(self, src, tgt=None):
        pass


# ------------------------------------------------------------------------------

