from fastscore.suite import Connect as ConnectBase
from fastscore.suite import Engine as EngineBase
from fastscore.suite import ModelManage as ModelManageBase

from .Engine import Engine
from .ModelManage import ModelManage

class Connect(ConnectBase):

    def __init__(self, proxy_prefix):
        """
        :param proxy_prefix: URL of the FastScore proxy endpoint
        """
        super(Connect, self).__init__(proxy_prefix)

    def get(self, name):
        """
        Retrieves a (cached) reference to the named instance.

        >>> mm = connect.get('model-manage-1')
        >>> mm.name
        'model-manage-1'

        :param name: a FastScore instance name.
        :returns: a FastScore instance object.
        """
        if name == 'connect':
            return self
        if name in self._resolved:
            return self._resolved[name]

        x = super(Connect, self).get(name)

        if isinstance(x, EngineBase):
            if isinstance(x, Engine):
                return x
            else:
                instance = Engine.from_base(x)
                self._resolved[name] = instance
                return instance
        elif isinstance(x, ModelManageBase):
            if isinstance(x, ModelManage):
                return x
            else:
                instance = ModelManage.from_base(x)
                self._resolved[name] = instance
                return instance
        
