from .base import * # noqa
from .mixins import * # noqa


class Server(RESTObject):
    pass


class Status(RESTObject):
    pass


class Version(RESTObject):
    pass


class VlanNode(RESTObject):
    pass


class Vlan(RESTObject):

    _managers = (
        ('nodes', 'NodeInVlanManager'),
    )

    @exc.on_http_error(exc.Grid5000GetError)
    def submit(self, data, **kwargs):
        path = "%s/%s" % (self.manager.path, self.get_id())
        self.manager.grid5000.http_post(path, post_data=data, **kwargs)


class Deployment(RESTObject, RefreshMixin):
    _create_attrs = (
        ('nodes', 'environment'),
        ('ssh_authorized_keys', 'version', 'client', 'custom_operations')
    )


class StorageHomeUser(RESTObject):
    pass


class StorageHome(RESTObject):
    _managers = (
        ('access', 'StorageHomeUserManager'),
    )


class Node(RESTObject):
    _managers = (
        ('versions', 'NodeVersionManager'),
    )


class Cluster(RESTObject):
    _managers = (
        ('nodes', 'NodeManager'),
        ('status', 'ClusterStatusManager'),
        ('versions', 'ClusterVersionManager')
    )


class Job(RESTObject, RefreshMixin, ObjectDeleteMixin):
    _create_attrs = (
        ("command"),
    )

    def __repr__(self):
        keys = ['uid', 'site', 'state', 'user']
        try:
            _repr = ["%s:%s" % (k, getattr(self, k)) for k in keys]
            return '<%s %s>' % (self.__class__.__name__, ' '.join(_repr))
        except:
           return super().__repr__()


class Site(RESTObject):
    _managers = (
        ('clusters', 'ClusterManager'),
        ('deployments', 'DeploymentManager'),
        ('jobs', 'JobManager'),
        ('servers', 'ServerManager'),
        ('status', 'SiteStatusManager'),
        ('storage', 'StorageHomeManager'),
        ('vlans', 'VlanManager'),
        ('vlansnodes', 'VlanNodeManager'),
        ('versions', 'SiteVersionManager')
    )


class Root(RESTObject):
    _managers = (
        ('sites', 'SiteManager'),
        ('versions', 'VersionManager')
    )


class RootManager(GetWithoutIdMixin, RESTManager):
    _path = '/'
    _obj_cls = Root


class SiteManager(RetrieveMixin, BracketMixin, RESTManager):
    _path = '/sites'
    _obj_cls = Site


class JobManager(NoUpdateMixin, BracketMixin, RESTManager):
    _path = '/sites/%(site)s/jobs'
    _obj_cls = Job
    _from_parent_attrs = {'site': 'uid'}


class ClusterManager(RetrieveMixin, BracketMixin, RESTManager):
    _path = '/sites/%(site)s/clusters'
    _obj_cls = Cluster
    _from_parent_attrs = {'site': 'uid'}


class NodeManager(RetrieveMixin, BracketMixin, RESTManager):
    _path = '/sites/%(site)s/clusters/%(cluster)s/nodes'
    _obj_cls = Node
    _from_parent_attrs = {'site': 'site', 'cluster': 'uid'}


class StorageHomeManager(RESTManager):
    _path = '/sites/%(site)s/storage/home'
    _obj_cls = StorageHome
    _from_parent_attrs = {'site': 'uid'}

    # NOTE(msimonin): grr ... need to fix the return values because it's not
    # consistent with the rest of API
    # So we fake a return value
    @exc.on_http_error(exc.Grid5000GetError)
    def __getitem__(self, key):
        return self._obj_cls(self, {"uid": key})


class StorageHomeUserManager(RESTManager):
    _path = '/sites/%(site)s/storage/home/%(user)s/access'
    _obj_cls = StorageHomeUser
    _from_parent_attrs = {'site': 'site', 'user': 'uid'}

    # NOTE(msimonin): grr ... need to fix the return values because it's not
    # consistent with the rest of API
    @exc.on_http_error(exc.Grid5000GetError)
    def list(self, **kwargs):
        """Retrieve a list of objects.

        The return value of the GET method is a dict:
        {
            "G5k-home_jpicard_j_1666466-nancy_1": {
                "ipv4": [
                    "172.16.64.97"
                ],
                "termination": {
                    "job": 1666466,
                    "site": "nancy"
                },
                "nfs_address": "srv-data.nancy.grid5000.fr:/export/home/picard"
            },
            "G5k-home_jpicard_u_1535456240_1": {
                "ipv4": [
                    "172.16.64.16"
                ],
                "termination": {
                    "until": 1535456240,
                },
                "nfs_address": "srv-data.nancy.grid5000.fr:/export/home/picard"
            }
        }
        We'd prefer having a list, so we inject an uid in the responses:
        [
            {
                "uid": "G5k-home_jpicard_j_1666466-nancy_1"
                "ipv4": [
                    "172.16.64.97"
                ],
                "termination": {
                    "job": 1666466,
                    "site": "nancy"
                },
                "nfs_address": "srv-data.nancy.grid5000.fr:/export/home/picard"
            },
        ]
        """
        l_objs = self.grid5000.http_get(self.path)
        _objs = []
        for uid, access in l_objs.items():
            _obj = access
            _obj.update(uid=uid)
            _objs.append(_obj)
        return [self._obj_cls(self, _obj) for _obj in _objs]

    @exc.on_http_error(exc.Grid5000CreateError)
    def create(self, data, **kwargs):
        """Create a new object.

        Args:
            data (dict): parameters to send to the server to create the
                         resource
            **kwargs: Extra options to send to the server

        Returns:
            RESTObject: a new instance of the managed object class built with
                the data sent by the server

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000CreateError: If the server cannot perform the request
        """

        # self._check_missing_create_attrs(data)

        # Handle specific URL for creation
        server_data = self.grid5000.http_post(self.path, post_data=data,
                                            **kwargs)
        return self._obj_cls(self, server_data)


class DeploymentManager(NoUpdateMixin, BracketMixin, RESTManager):
    _path = '/sites/%(site)s/deployments'
    _obj_cls = Deployment
    _from_parent_attrs = {'site': 'uid'}


class VlanManager(RetrieveMixin, BracketMixin, RESTManager):
    _path = '/sites/%(site)s/vlans'
    _obj_cls = Vlan
    _from_parent_attrs = {'site': 'uid'}


class VlanNodeManager(ListMixin, RESTManager):
    _path = '/sites/%(site)s/vlans/nodes'
    _obj_cls = VlanNode
    _from_parent_attrs = {'site': 'uid'}

    @exc.on_http_error(exc.Grid5000GetError)
    def submit(self, data, **kwargs):

        def _to_kavlan(node, vlan):
            n = node.split('.')
            n[0] = '%s-kavlan-%s' % (n[0], vlan)
            return '.'.join(n)

        server_data = self.grid5000.http_post(self.path,
                                              post_data=data,
                                              **kwargs)
        # this returns a dict k=node, v=vlanid
        # we generate the kavlan fqdn as uid
        return [self._obj_cls(self, {'uid': _to_kavlan(node, vlan),
                                     'node': node,
                                     'vlan': vlan})
                for node, vlan in server_data.items()]


class NodeInVlanManager(RESTManager):
    _path = '/sites/%(site)s/vlans/%(vlan_id)s/nodes'
    _obj_cls = VlanNode
    _from_parent_attrs = {'site': 'site', 'vlan_id': 'uid'}

    @exc.on_http_error(exc.Grid5000ListError)
    def list(self, **kwargs):
        """
        We got this kind of answere (which isn't a list as one could expect)
        {
            'uid': 'nodes',
            'nodes': ['paranoia-8-eth2.rennes.grid5000.fr'],
            'links': [...]
        }
        """
        data = kwargs.copy()
        path = data.pop('path', self.path)
        server_data = self.grid5000.http_list(path, **data)
        return [self._obj_cls(self, {'uid': node})
                for node in server_data['nodes']]


class VersionManager(RESTManager, BracketMixin, RetrieveMixin):
    _path = '/versions'
    _obj_cls = Version


class SiteVersionManager(RESTManager, BracketMixin, RetrieveMixin):
    _path = '/sites/%(site)s/versions'
    _obj_cls = Version
    _from_parent_attrs = {'site': 'uid'}


class ClusterVersionManager(RESTManager, BracketMixin, RetrieveMixin):
    _path = '/sites/%(site)s/clusters/%(cluster)s/versions'
    _obj_cls = Version
    _from_parent_attrs = {'site': 'site', 'cluster': 'uid'}


class NodeVersionManager(RESTManager, BracketMixin, RetrieveMixin):
    _path = '/sites/%(site)s/clusters/%(cluster)s/nodes/%(node)s/versions'
    _obj_cls = Version
    _from_parent_attrs = {'site': 'site', 'cluster': 'cluster', 'node': 'uid'}


class SiteStatusManager(RESTManager, RetrieveMixin):
    _path = '/sites/%(site)s/status'
    _obj_cls = Status
    _from_parent_attrs = {'site': 'uid'}


class ClusterStatusManager(RESTManager, RetrieveMixin):
    _path = '/sites/%(site)s/clusters/%(cluster)s/status'
    _obj_cls = Status
    _from_parent_attrs = {'site': 'site', 'cluster': 'uid'}


class ServerManager(RESTManager, BracketMixin, RetrieveMixin):
    _path = '/sites/%(site)s/servers'
    _obj_cls = Server
    _from_parent_attrs = {'site': 'uid'}
