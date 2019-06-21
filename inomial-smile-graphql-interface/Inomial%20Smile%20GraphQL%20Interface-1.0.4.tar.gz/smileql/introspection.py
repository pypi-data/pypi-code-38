import logging


class Builder:
    """
    Looks over the graphsql schema and provides model building of the relevant data
    """

    def __init__(self, parent, api):
        self._api = api
        self._parent = parent
        self._log = logging.getLogger(self.__class__.__name__)
        self._lookup_schema_types()

    def _lookup_schema_types(self):
        for objectDeclaration in self._api.client.introspection.get("__schema", {}).get(
            "types", []
        ):
            getattr(self, f"_set_{objectDeclaration['kind']}")(objectDeclaration)

    def _set_INPUT_OBJECT(self, obj):
        """Sets the input type object for a mutation"""
        # self._log.debug(obj["name"])
        pass

    def _set_OBJECT(self, obj):
        """ Sets an object that represent something queriable"""
        self._log.debug(obj["name"])
        cls = type(
            obj["name"],
            (object,),
            dict(**{"__doc__": obj["description"], "__kind__": obj["kind"]}, **obj),
        )
        setattr(self._parent, obj["name"], cls)

    def _set_SCALAR(self, obj):
        # self._log.debug(obj["name"])
        pass

    def _set_ENUM(self, obj):
        # self._log.debug(obj["name"])
        pass
