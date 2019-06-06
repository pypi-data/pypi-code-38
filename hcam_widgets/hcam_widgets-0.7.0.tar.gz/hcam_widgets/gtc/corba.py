import CosNaming
from omniORB import CORBA
# not part of this module, copy modules from GCS and place in PYTHONPATH
import HIPERTELESCOPESERVER
import os


def get_telescope_server():
    conn = CORBAConnection()
    conn.init_orb()
    conn.resolve_nameservice()

    # name of CORBA object to access telescope server
    # TODO: change to correct name
    name = [CosNaming.NameComponent(id='HIPERTelescopeServer', kind='')]

    server = conn.get_object(name, HIPERTELESCOPESERVER.HIPERTelescopeServer_ifce)
    return server


class CORBAConnection(object):
    """
    A class to handle communication with the GTC CORBA system.

    Simply delegates the relevant operations to the current state object.
    """
    def __init__(self):
        self.new_state(RawCORBAState)

    def new_state(self, state):
        # change the class to a concrete type
        self._state = state

    def init_orb(self):
        self._state.init_orb(self)

    def resolve_nameservice(self):
        self._state.resolve_nameservice(self)

    def get_object(self, binding_name, cls):
        """
        Get a reference to a remote object using CORBA
        """
        return self._state.get_object(self, binding_name, cls)


class RawCORBAState(object):
    """
    A CORBA state just after creation, with no ORB or nameservice
    """
    @staticmethod
    def init_orb(conn):
        # setup CORBA, TODO put correct GTC host here
        os.environ['ORBDefaultInitRef'] = 'corbaname::161.72.88.75:12008'
        os.environ['ORBclientCallTimeOutPeriod'] = '2000'  # in milliseconds
        orb = CORBA.ORB_init([], CORBA.ORB_ID)
        conn.orb = orb
        conn.new_state(InitialisedCORBAState)

    @staticmethod
    def resolve_nameservice(conn):
        raise RuntimeError('ORB not initialised')

    @staticmethod
    def get_object(conn, binding_name, cls):
        """
        Get a reference to a remote object using CORBA
        """
        raise RuntimeError('ORB not initialised')


class InitialisedCORBAState(object):
    """
    A CORBA state just after creation, with no ORB or nameservice
    """
    @staticmethod
    def init_orb(conn):
        raise RuntimeError('ORB already initialised')

    @staticmethod
    def resolve_nameservice(conn):
        # get instance of nameserver from GTC CORBA sever
        try:
            obj = conn.orb.resolve_initial_references('NameService')
            rootContext = obj._narrow(CosNaming.NamingContext)
        except CORBA.TRANSIENT:
            raise IOError('could not connect to GTC CORBA NameServer')

        if rootContext is None:
            raise IOError('attempt to get NameServer from GTC failed')
        conn.rootContext = rootContext
        conn.new_state(ReadyCORBAState)

    @staticmethod
    def get_object(conn, binding_name, cls):
        """
        Get a reference to a remote object using CORBA
        """
        raise RuntimeError('NameService needs to be resolved first')


class ReadyCORBAState(object):
    """
    A CORBA state which is ready to retrieve objects
    """
    @staticmethod
    def init_orb(conn):
        raise RuntimeError('ORB already initialised')

    @staticmethod
    def resolve_nameservice(conn):
        # get instance of nameserver from GTC CORBA sever
        raise RuntimeError('NameService already resolved')

    @staticmethod
    def get_object(conn, binding_name, object_cls):
        """
        Get a reference to a remote object using CORBA
        """
        try:
            obj = conn.rootContext.resolve(binding_name)
            narrowed = obj._narrow(object_cls)
        except CORBA.TRANSIENT:
            raise IOError('Attempt to retrieve object failed')

        if narrowed is None:
            raise IOError('Attempt to retrieve object got a different class of object')

        return narrowed
