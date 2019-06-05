import importlib
import json


class RESTManager(object):
    """Base class for CRUD operations on objects.

    Derivated class must define ``_path`` and ``_obj_cls``.

    ``_path``: Base URL path on which requests will be sent (e.g. '/projects')
    ``_obj_cls``: The class of objects that will be created
    """

    _path = None
    _obj_cls = None

    def __init__(self, gk, parent=None):
        """REST manager constructor.

        Args:
            gl (Grid5000): :class:`~gitlab.Grid5000` connection to use to make
                         requests.
            parent: REST object to which the manager is attached.
        """
        self.grid5000 = gk
        self._parent = parent  # for nested managers
        self._computed_path = self._compute_path()

    @property
    def parent_attrs(self):
        return self._parent_attrs

    def _compute_path(self, path=None):
        self._parent_attrs = {}
        if path is None:
            path = self._path
        if self._parent is None or not hasattr(self, '_from_parent_attrs'):
            return path
        data = {self_attr: getattr(self._parent, parent_attr, None)
                for self_attr, parent_attr in self._from_parent_attrs.items()}
        self._parent_attrs = data
        return path % data

    @property
    def path(self):
        return self._computed_path


class RESTObject(object):
    """Represents an object built from server data.

    It holds the attributes know from the server, and the updated attributes in
    another. This allows smart updates, if the object allows it.

    You can redefine ``_id_attr`` in child classes to specify which attribute
    must be used as uniq ID. ``None`` means that the object can be updated
    without ID in the url.
    """
    _id_attr = 'uid'

    def __init__(self, manager, attrs):
        self.__dict__.update({
            'manager': manager,
            '_attrs': attrs,
            '_updated_attrs': {},
            '_module': importlib.import_module(self.__module__)
        })
        self.__dict__['_parent_attrs'] = self.manager.parent_attrs
        self._create_managers()

    def __getstate__(self):
        state = self.__dict__.copy()
        # module can't be pickled
        module = state.pop('_module')
        state['_module_name'] = module.__name__
        return state

    def __setstate__(self, state):
        module_name = state.pop('_module_name')
        self.__dict__.update(state)
        self.__dict__.update(_module=importlib.import_module(module_name))

    def __getattr__(self, name):
        try:
            return self.__dict__['_updated_attrs'][name]
        except KeyError:
            try:
                value = self.__dict__['_attrs'][name]

                # If the value is a list, we copy it in the _updated_attrs dict
                # because we are not able to detect changes made on the object
                # (append, insert, pop, ...). Without forcing the attr
                # creation __setattr__ is never called, the list never ends up
                # in the _updated_attrs dict, and the update() and save()
                # method never push the new data to the server.
                # See https://github.com/python-gitlab/python-gitlab/issues/306
                #
                # note: _parent_attrs will only store simple values (int) so we
                # don't make this check in the next except block.
                if isinstance(value, list):
                    self.__dict__['_updated_attrs'][name] = value[:]
                    return self.__dict__['_updated_attrs'][name]

                return value

            except KeyError:
                try:
                    return self.__dict__['_parent_attrs'][name]
                except KeyError:
                    raise AttributeError(name)

    def __setattr__(self, name, value):
        self.__dict__['_updated_attrs'][name] = value

    def __str__(self):
        data = self._attrs.copy()
        data.update(self._updated_attrs)
        return '%s => \n %s' % (type(self), json.dumps(data, indent=4))

    def __repr__(self):
        if self._id_attr:
            return '<%s %s:%s>' % (self.__class__.__name__,
                                   self._id_attr,
                                   self.get_id())
        else:
            return '<%s>' % self.__class__.__name__

    def _create_managers(self):
        managers = getattr(self, '_managers', None)
        if managers is None:
            return

        for attr, cls_name in self._managers:
            cls = getattr(self._module, cls_name)
            manager = cls(self.manager.grid5000, parent=self)
            self.__dict__[attr] = manager

    def _update_attrs(self, new_attrs):
        self.__dict__['_updated_attrs'] = {}
        self.__dict__['_attrs'].update(new_attrs)

    def get_id(self):
        """Returns the id of the resource."""
        if self._id_attr is None:
            return None
        return getattr(self, self._id_attr)

    @property
    def attributes(self):
        d = self.__dict__['_updated_attrs'].copy()
        d.update(self.__dict__['_attrs'])
        d.update(self.__dict__['_parent_attrs'])
        return d
