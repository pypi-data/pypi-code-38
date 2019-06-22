from pyrediseasyio.io.io_group import IOGroup
from pyrediseasyio.html.html_io import HTMLIO
from typing import List, Callable
from dominate.tags import div, table
import json


class HMTLIOGroup:

    def __init__(self, io_group: IOGroup,
                 html_id_header: str,
                 namespace: str = 'pyredeio'):

        self.html_id_header = html_id_header
        self._io_group = io_group
        self.namespace = namespace

    @property
    def html_id(self):
        return f'{self.html_id_header}_io_container'

    def html(self, by_names: List = None, by_type: List = None,
             by_lambda_each: Callable = None, by_lambda_results: Callable = None,
             html_classes: List = None):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)
        cls = f'{self.namespace}_io_container'
        classes = html_classes.append(cls) if html_classes else [cls]
        classes = ' '.join(classes)

        with div(cls=classes, id=self.html_id) as container:
            for attr in attrs:
                HTMLIO(attr, self.html_id_header, self.namespace).html()
        return container

    def html_table(self, by_names: List = None, by_type: List = None,
                   by_lambda_each: Callable = None, by_lambda_results: Callable = None,
                   html_classes: List = None, show_units: bool=True):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)
        cls = f'{self.namespace}_io_container'
        classes = html_classes.append(cls) if html_classes else [cls]
        classes = ' '.join(classes)

        with table(cls=classes, id=self.html_id) as container:
            for attr in attrs:
                HTMLIO(attr, self.html_id_header, self.namespace).html_row(show_units)
        return container

    def dumps(self, by_names: List = None, by_type: List = None,
              by_lambda_each: Callable = None, by_lambda_results: Callable = None):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)

        def f(a):
            return dict(id=HTMLIO.html_id_for(self.html_id_header, a), name=a.name, value=a.value, units=a.units)
        results = [f(a) for a in attrs]

        return json.dumps(results)


