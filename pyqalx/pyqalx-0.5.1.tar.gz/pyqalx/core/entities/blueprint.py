from pyqalx.core.entities import QalxEntity, Item, Set
from pyqalx.core.errors import QalxInvalidBlueprintError


class Blueprint(QalxEntity):
    entity_type = 'blueprint'

    def _update_property(self, property_key, key, schema_value, required=False):
        self['properties'][property_key]['properties'][key] = schema_value
        if (required is True) and (key not in self['properties'][property_key]['required']):
            self['properties'][property_key]['required'].append(key)
        return self

    @classmethod
    def _base_blueprint(cls):
        return cls({
            'type': 'object',
            'properties': {
                'meta': {'type': 'object',
                         'properties': {},
                         'required': []
                         }
            },
        })

    @classmethod
    def item(cls):
        """
        A blueprint that gives the default blueprint structure for an
        `entities.item.Item` entity
        """
        blueprint = cls._base_blueprint()
        blueprint['entity_type'] = Item.entity_type
        blueprint['properties']['data'] = {'type': 'object',
                                           'properties': {},
                                           'required': []
                                           }
        blueprint['required'] = ['data']
        return blueprint

    @classmethod
    def set(cls):
        """
        A blueprint that gives the default blueprint structure for an
        `entities.set.Set` entity
        """
        blueprint = cls._base_blueprint()
        blueprint['entity_type'] = Set.entity_type
        blueprint['properties']['items'] = {'type': 'object',
                                            'properties': {},
                                            'required': []
                                            }
        blueprint['required'] = ['items']
        return blueprint

    def add_data(self, key, schema_value, required=False):
        """
        Adds data to this item blueprint instance.
        :param key: The key in the data you want to add
        :param schema_value: The schema value you want to add
        :return: An updated instance of the item blueprint
        """
        return self._update_property(property_key='data',
                                     key=key,
                                     schema_value=schema_value,
                                     required=required)

    def add_meta(self, key, schema_value, required=False):
        """
        Adds meta to this item blueprint instance.
        :param key: The key in the meta you want to add
        :param schema_value: The schema value you want to add
        :return: An updated instance of the item blueprint
        """
        return self._update_property(property_key='meta',
                                     key=key,
                                     schema_value=schema_value,
                                     required=required)

    def add_item(self, key, item_blueprint=None, required=False):
        """
        Adds an item to this set blueprint instance.  If `item_blueprint` is
        provided then the set schema will always require that specific
        item blueprint for `key`.  If `item_blueprint` is not provided then
        the set blueprint will accept any data for `key` when being used
        :param key: They `key` of the item you want the blueprint to validate
        :type key: str
        :param item_blueprint: If provided will save the `name` from the
        blueprint against the `key`.  This means that whenever the set is created you must use the same blueprint.
        :type item_blueprint: str
        :return: An updated instance of the set blueprint
        """
        if item_blueprint is None:
            # the data stored against `key` can be anything when the set is
            # created
            schema_value = {'type': 'object'}
        else:
            # the data stored against `key` must match the item blueprint
            if not isinstance(item_blueprint, self.__class__):
                raise QalxInvalidBlueprintError(f'`{item_blueprint}` is not an'
                                                f' instance of `{self.__class__}`')
            schema_value = {
                'type': 'string',
                'enum': [item_blueprint['name']]
            }
        return self._update_property(property_key='items',
                                     key=key,
                                     schema_value=schema_value,
                                     required=required)
