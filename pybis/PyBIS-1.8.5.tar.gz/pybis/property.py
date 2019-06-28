from tabulate import tabulate
from texttable import Texttable
from pybis.utils import check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl

class PropertyHolder():

    def __init__(self, openbis_obj, type=None):
        self.__dict__['_openbis'] = openbis_obj
        self.__dict__['_property_names'] = {}
        if type is not None:
            self.__dict__['_type'] = type
            for prop in type.data['propertyAssignments']:
                property_name = prop['propertyType']['code'].lower()
                self._property_names[property_name]=prop['propertyType']
                self._property_names[property_name]['mandatory'] = prop['mandatory']
                self._property_names[property_name]['showInEditView'] = prop['showInEditView']

    def _get_terms(self, vocabulary):
        return self._openbis.get_terms(vocabulary)

    def _all_props(self):
        props = {}
        for code in self._type.codes():
            props[code] = getattr(self, code)
        return props

    def all(self):
        """Returns the properties as an array
        """
        props = {}
        for code in self._type.codes():
            props[code] = getattr(self, code)
        return props

    def all_nonempty(self):
        props = {}
        for code in self._type.codes():
            value = getattr(self, code)
            if value is not None:
                props[code] = value
        return props

    def __getitem__(self, key):
        """For properties that contain either a dot or a dash or any other non-valid method character,
        a user can use a key-lookup instead, e.g. sample.props['my-weird.property-name']
        """
        return getattr(self, key)

    def __getattr__(self, name):
        """ attribute syntax can be found out by
            adding an underscore at the end of the property name
        """ 
        if name == '_ipython_canary_method_should_not_exist_':
            # make Jupyter use the _repr_html_ method
            return
        if name.endswith('_'):
            name = name.rstrip('_')
            if name in self._property_names:
                property_type = self._property_names[name]
                if property_type['dataType'] == 'CONTROLLEDVOCABULARY':
                    return self._get_terms(property_type['vocabulary']['code'])
                else:
                    syntax = { property_type["label"] : property_type["dataType"]}
                    if property_type["dataType"] == "TIMESTAMP":
                        syntax['syntax'] = 'YYYY-MM-DD HH:MIN:SS'
                    return syntax
            else:
                return

    def __setattr__(self, name, value):
        """This special method allows a PropertyHolder object
        to check the attributes that are assigned to that object
        """
        if name not in self._property_names:
            raise KeyError(
                "No such property: '{}'. Allowed properties are: {}".format(
                    name, ", ".join(self._property_names.keys())
                )
            )
        property_type = self._property_names[name]
        data_type = property_type['dataType']
        if data_type == 'CONTROLLEDVOCABULARY':
            voc = self._get_terms(property_type['vocabulary']['code'])
            value = str(value).upper()
            if value not in voc.df['code'].values:
                raise ValueError("Value for attribute {} must be one of these terms: {}".format(
                    name, ", ".join(voc.df['code'].values)
                ))
        elif data_type in ('INTEGER', 'BOOLEAN', 'VARCHAR'):
            if not check_datatype(data_type, value):
                raise ValueError("Value must be of type {}".format(data_type))
        self.__dict__[name] = value

    def __setitem__(self, key, value):
        """For properties that contain either a dot or a dash or any other non-valid method character,
        a user can use a key instead, e.g. sample.props['my-weird.property-name']
        """
        return setattr(self, key, value)

    def __dir__(self):
        return self._property_names

    def _repr_html_(self):
        def nvl(val, string=''):
            if val is None:
                return string
            elif val == 'true':
                return True
            elif val == 'false':
                return False
            return val
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>property</th>
                <th>value</th>
                <th>description</th>
                <th>type</th>
                <th>mandatory</th>
                </tr>
            </thead>
            <tbody>
        """

        for prop_name, prop in self._property_names.items():
            html += "<tr> <td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td> </tr>".format(
                prop_name, nvl(getattr(self, prop_name, ''),''),
                prop.get('description'),
                prop.get('dataType'),
                prop.get('mandatory'),
            )

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):
        def nvl(val, string=''):
            if val is None:
                return string
            elif val == 'true':
                return True
            elif val == 'false':
                return False
            return str(val)

        headers = ['property', 'value', 'mandatory']

        lines = []
        for prop_name in self._property_names:
            lines.append([
                prop_name,
                nvl(getattr(self, prop_name, ''))
            ])
        return tabulate(lines, headers=headers)

