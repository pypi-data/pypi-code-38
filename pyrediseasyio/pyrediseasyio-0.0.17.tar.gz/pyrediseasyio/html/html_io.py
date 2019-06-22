from pyrediseasyio.io.base import SingleIO
from dominate.tags import div, tr, td


class HTMLIO:

    def __init__(self, io: SingleIO, namespace: str='easyio'):
        self.io = io
        self.namespace = namespace
        self.html_class = f'{self.namespace}_io'
        self.name = io.name
        self.val = io.value
        self.addr = io.addr
        self.units = io.units
        self.html_id = f'{self.addr}_io_value'

    def html(self, show_units: bool = True):
        io = self.io
        name, addr, val, units = io.name, io.addr, io.value, io.units
        with div(cls=self.html_class, id=addr) as container:
            div(name, cls=f'{self.html_class}_name')
            div(val, cls=f'{self.html_class}_value', id=self.html_id, onchange='OnIOValueChange(event)')
            if show_units:
                units = '' if units is None else units
                div(units, cls=f'{self.html_class}_units')
        return container

    def html_row(self, show_units: bool = True):
        io = self.io
        name, addr, val, units = io.name, io.addr, io.value, io.units
        with tr(cls=self.html_class, id=addr) as container:
            td(name, cls=f'{self.html_class}_name')
            td(val, cls=f'{self.html_class}_value', id=self.html_id, onchange='OnIOValueChange(event)')
            if show_units:
                units = '' if units is None else units
                td(units, cls=f'{self.html_class}_units')
        return container







