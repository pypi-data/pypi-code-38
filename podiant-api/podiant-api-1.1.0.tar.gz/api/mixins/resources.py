class ResourceMixin(object):
    def get_resource_kwargs(self):  # pragma: no cover
        """
        This method returns a dictionary of kwargs to be passed when
        instantiating a resource or resource list.
        """

        return {}

    def get_resource(self):
        """
        Helper method to return the resource for this view. Requires the
        setting of a `resource_class` property.
        """

        if not hasattr(self, '_resource_cache'):
            self._resource_cache = self.resource_class(
                **self.get_resource_kwargs()
            )

        return self._resource_cache
