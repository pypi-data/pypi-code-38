import grid5000.exceptions as exc


class GetMixin(object):
    @exc.on_http_error(exc.Grid5000GetError)
    def get(self, id, **kwargs):
        """Retrieve a single object.

        Args:
            id (int or str): ID of the object to retrieve
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            object: The generated RESTObject.

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000GetError: If the server cannot perform the request
        """
        if not isinstance(id, int):
            id = id.replace('/', '%2F')
        path = '%s/%s' % (self.path, id)
        server_data = self.grid5000.http_get(path, **kwargs)
        return self._obj_cls(self, server_data)


class GetWithoutIdMixin(object):
    @exc.on_http_error(exc.Grid5000GetError)
    def get(self, id=None, **kwargs):
        """Retrieve a single object.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            object: The generated RESTObject

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000GetError: If the server cannot perform the request
        """
        server_data = self.grid5000.http_get(self.path, **kwargs)
        if server_data is None:
            return None
        return self._obj_cls(self, server_data)


class RefreshMixin(object):
    @exc.on_http_error(exc.Grid5000GetError)
    def refresh(self, **kwargs):
        """Refresh a single object from server.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns None (updates the object)

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000GetError: If the server cannot perform the request
        """
        if self._id_attr:
            path = '%s/%s' % (self.manager.path, self.get_id())
        else:
            path = self.manager.path
        server_data = self.manager.grid5000.http_get(path, **kwargs)
        self._update_attrs(server_data)


class ListMixin(object):
    @exc.on_http_error(exc.Grid5000ListError)
    def list(self, **kwargs):
        """Retrieve a list of objects.

        Args:
            all (bool): If True, return all the items, without pagination
            per_page (int): Number of items to retrieve per request
            page (int): ID of the page to return (starts with page 1)
            as_list (bool): If set to False and no pagination option is
                defined, return a generator instead of a list
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            list: The list of objects, or a generator if `as_list` is False

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000ListError: If the server cannot perform the request
        """

        # Duplicate data to avoid messing with what the user sent us
        data = kwargs.copy()
        # We get the attributes that need some special transformation
        types = getattr(self, '_types', {})
        if types:
            for attr_name, type_cls in types.items():
                if attr_name in data.keys():
                    type_obj = type_cls(data[attr_name])
                    data[attr_name] = type_obj.get_for_api()

        # Allow to overwrite the path, handy for custom listings
        path = data.pop('path', self.path)
        l_obj = self.grid5000.http_list(path, **data)

        if isinstance(l_obj, list):
            return [self._obj_cls(self, item) for item in l_obj]
        elif isinstance(l_obj, dict):
            return self._obj_cls(self, l_obj)
        else:
            raise exc.Grid5000ListError(
                "Returned value is neither a list nor a dict")


class CreateMixin(object):
    def _check_missing_create_attrs(self, data):
        required, optional = self.get_create_attrs()
        missing = []
        for attr in required:
            if attr not in data:
                missing.append(attr)
                continue
        if missing:
            raise AttributeError("Missing attributes: %s" % ", ".join(missing))

    def get_create_attrs(self):
        """Return the required and optional arguments.

        Returns:
            tuple: 2 items: list of required arguments and list of optional
                   arguments for creation (in that order)
        """
        return getattr(self, '_create_attrs', (tuple(), tuple()))

    @exc.on_http_error(exc.Grid5000CreateError)
    def create(self, data, **kwargs):
        """Create a new object.

        Args:
            data (dict): parameters to send to the server to create the
                         resource
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            RESTObject: a new instance of the managed object class built with
                the data sent by the server

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000CreateError: If the server cannot perform the request
        """
        self._check_missing_create_attrs(data)

        # Handle specific URL for creation
        server_data = self.grid5000.http_post(self.path, post_data=data,
                                            **kwargs)
        return self._obj_cls(self, server_data)


class DeleteMixin(object):
    @exc.on_http_error(exc.Grid5000DeleteError)
    def delete(self, id, **kwargs):
        """Delete an object on the server.

        Args:
            id: ID of the object to delete
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000DeleteError: If the server cannot perform the request
        """
        if id is None:
            path = self.path
        else:
            if not isinstance(id, int):
                id = id.replace('/', '%2F')
            path = '%s/%s' % (self.path, id)
        self.grid5000.http_delete(path, **kwargs)


class BracketMixin(object):
    @exc.on_http_error(exc.Grid5000GetError)
    def __getitem__(self, key):
        """Because that reminds me about RESTfully."""
        path = '%s/%s' % (self.path, key)
        server_data = self.grid5000.http_get(path)
        return self._obj_cls(self, server_data)


class ObjectDeleteMixin(object):
    """Mixin for RESTObject's that can be deleted."""
    def delete(self, **kwargs):
        """Delete the object from the server.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            Grid5000AuthenticationError: If authentication is not correct
            Grid5000DeleteError: If the server cannot perform the request
        """
        self.manager.delete(self.get_id())


# Composite Mixins
class RetrieveMixin(ListMixin, GetMixin):
    pass


class NoUpdateMixin(GetMixin, ListMixin, CreateMixin, DeleteMixin):
    pass
