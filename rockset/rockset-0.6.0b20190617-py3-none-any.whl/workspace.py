"""
Usage
-----
Workspace objects repesents a container of other workspaces and
Rockset collections. 

Example
-------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client()

    # create a workspace
    rs.Workspace.create('marketing')

    # create a collection in the workspace
    user_events = rs.Collection.create('user_events', workspace='marketing')

.. _Collection.create:

Create a new workspace 
-----------------------
Creating a workspace using the Client_ object is as simple as
calling ``client.Workspace.create("my-new-workspace")``::

    from rockset import Client
    rs = Client()
    new_collection = rs.Workspace.create("my-new-workspace")

.. _Workspace.list:

List all workspaces 
--------------------
List all workspaces using the Client_ object using::

    from rockset import Client
    rs = Client()
    collections = rs.Workspace.list()

.. _Workspace.retrieve:

Retrieve an existing workspace 
-------------------------------
Retrive a workspace to run various operations on that workspace::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('marketing')

.. _Workpace.drop:

Drop a workspace 
-----------------
Use the ``drop()`` method to remove a workspace permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()
    marketing = rs.Workspace.retrieve('marketing')
    marketing.drop()

"""
from .exception import InputError

from rockset.swagger_client.api import (WorkspacesApi)
from rockset.swagger_client.models import (
    CreateWorkspaceRequest
)


class Workspace():
    @classmethod
    def create(
        cls,
        name,
        description=None,
        **kwargs
    ):
        """Creates a new Rockset workspace.

        Use it via rockset.Client().Workspace.create()

        Only alphanumeric characters, ``_``, ``-`` and ``.`` are allowed
        in collection paths. Including a ``.`` will create every parent workspace
        along the path if it does not already exist.

        Args:
            name (str): name of the workspace to be created.
            description (str): a human readable description of the workspace
        Returns:
            Workspace: Workspace object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Workspace.create() instead.'
            )
        client = kwargs.pop('client')

        kwargs['description'] = description

        req = CreateWorkspaceRequest(name=name, **kwargs)
        workspace = WorkspacesApi(client).create(
            body=req
        ).get('data').to_dict()

        return cls(client=client, **workspace)

    @classmethod
    def retrieve(cls, name, **kwargs):
        """Retrieves details of a single workspace 

        Use it via rockset.Client().Workspace.retrieve()

        Args:
            name (str): Name of the workspace 

        Returns:
            Workspace: Workspace object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Workspace.create() instead.'
            )
        w = cls(name=name, **kwargs)

        return w

    @classmethod
    def list(cls, **kwargs):
        """Returns list of all workspaces.

        Use it via rockset.Client().Workspace.list()

        Returns:
            List: A list of Workspace objects
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.list() instead.'
            )
        client = kwargs.pop('client')

        if 'workspace' in kwargs:
            workspaces = WorkspacesApi(client).child(workspace=kwargs.pop('workspace')).get('data')
        else:
            workspaces = WorkspacesApi(client).list().get('data')

        ret = []
        for w in workspaces:
            if type(w) is dict:
                ret.append(cls(client=client, **w))
            else:
                ret.append(cls(client=client, **w.to_dict()))

        return ret

    def __init__(self, client, name, **kwargs):
        """Represents a single Workspace"""
        self.client = client
        self.name = name
        self.type = 'WORKSPACE'
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return

    # instance methods
    def drop(self):
        """Deletes the workspace represented by this object."""
        WorkspacesApi(self.client).delete(workspace=self.name)
        return

__all__ = [
    'Workspace',
]
