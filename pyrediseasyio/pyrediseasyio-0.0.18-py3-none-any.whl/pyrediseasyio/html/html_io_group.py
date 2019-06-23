from pyrediseasyio.io.io_group import IOGroup
from pyrediseasyio.html.html_io import HTMLIO
from typing import List, Callable
from dominate.tags import div, table, tr, th
import json


class HMTLIOGroup:

    def __init__(self, io_group: IOGroup, html_id: str = None):
        self._io_group = io_group
        self.namespace = io_group.namespace
        self.html_id = html_id



    def html(self, by_names: List = None, by_type: List = None,
             by_lambda_each: Callable = None, by_lambda_results: Callable = None,
             html_classes: List = None, show_units: bool=True):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)
        cls = f'easyio_io_container'
        classes = html_classes.append(cls) if html_classes else [cls]
        classes = ' '.join(classes)
        html_id = f'{attrs[0].key}_io_container' if self.html_id is None else self.html_id

        with div(cls=classes, id=html_id) as container:
            for attr in attrs:
                HTMLIO(attr).html(show_units)
        return container



    def html_table(self, by_names: List = None, by_type: List = None,
                   by_lambda_each: Callable = None, by_lambda_results: Callable = None,
                   html_classes: List = None, show_units: bool = True,
                   headers: List = None):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)
        cls = f'{self.namespace}_io_container'
        classes = html_classes.append(cls) if html_classes else [cls]
        classes = ' '.join(classes)
        html_id = f'{attrs[0].addr}_io_container' if self.html_id is None else self.html_id

        with table(cls=classes, id=html_id) as container:
            if headers:
                with tr():
                    for h in headers:
                        th(h)
            for attr in attrs:
                HTMLIO(attr).html_row(show_units)
        return container



    def dumps(self, by_names: List = None, by_type: List = None,
              by_lambda_each: Callable = None, by_lambda_results: Callable = None):

        attrs = self._io_group.get_attributes(by_names, by_type, by_lambda_each, by_lambda_results)

        def f(a):
            io = HTMLIO(a)
            return dict(id=io.value_id, name=io.name, value=io.value, units=io.units)
        results = [f(a) for a in attrs]

        return json.dumps(results)


