from .openbis_object import OpenBisObject 
from .definitions import openbis_definitions, fetch_option
from .utils import VERBOSE
from .attribute import AttrHolder
import json

class Plugin(OpenBisObject):
    """ 
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['entity'] = 'Plugin'
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, self.entity)

        if data is not None:
            self.a(data)

        attrs_new = openbis_definitions(self.entity)['attrs_new']
        if kwargs is not None:
            for attr in kwargs:
                if attr not in attrs_new:
                    raise ValueError("unknown attribute: {}".format(attr))
                else:
                    setattr(self, attr, kwargs[attr])

    def __dir__(self):
        return [
            'name','description','script'
        ]

    def delete(self, reason='no reason'):
        self.openbis.delete_entity(entity=self.entity,id=self.permId, reason=reason)
        if VERBOSE: print("Plugin {} successfully deleted.".format(self.permId))

    def save(self):

        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Plugin successfully created.")
            new_tag_data = self.openbis.get_tag(resp[0]['permId'], only_data=True)
            self._set_data(new_tag_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Plugin successfully updated.")
            new_tag_data = self.openbis.get_tag(self.permId, only_data=True)
            self._set_data(new_tag_data)


    def _repr_html_(self):
        """ creates a nice table in Jupyter notebooks when the object itself displayed
        """
        def nvl(val, string=''):
            if val is None:
                return string
            return val

        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self._allowed_attrs:
            if attr in ['script']:
                continue
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, nvl(getattr(self, attr, ''), '')
            )

        html += """
            </tbody>
            </table>
            <br/>
        """

        if self.script is not None:
            html += "<b>Script</b>"
            for line in self.script.split('\n'):
                html += '<pre class=" CodeMirror-line ">{}</pre>'.format(line)
        else:
            html += "<b>No Script defined.</b>"

        return html
