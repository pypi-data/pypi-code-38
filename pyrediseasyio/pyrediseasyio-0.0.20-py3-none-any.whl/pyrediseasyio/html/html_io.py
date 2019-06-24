from pyrediseasyio.io.single_io import SingleIO
from dominate.tags import div, tr, td


class HTMLIO:

    def __init__(self, io: SingleIO):
        key = io.key
        self.io = io
        self.container_id = f'{key}_io'
        self.value_id = f'{key}'
        self.name = io.name
        self.value = io.value
        self.units = io.units



    def html(self, show_units: bool = True):
        io = self.io
        name, addr, val, units, ns = io.name, io.addr, io.value, io.units, io.namespace
        with div(cls='easyio_io', id=self.container_id) as container:
            div(name, cls='easyio_name')
            div(val, cls=f'easyio_value', id=self.value_id, onchange='OnIOValueChange(event)',
                data_namespace=ns, data_addr=addr)
            if show_units:
                units = '' if units is None else units
                div(units, cls=f'easyio_units')
        return container



    def html_row(self, show_units: bool = True):
        io = self.io
        name, addr, val, units, ns = io.name, io.addr, io.value, io.units, io.namespace
        with tr(cls='easyio_io', id=self.container_id) as container:
            td(name, cls='easyio_name')
            td(val, cls=f'easyio_value', id=self.value_id, onchange='OnIOValueChange(event)',
               data_namespace=ns, data_addr=addr)
            if show_units:
                units = '' if units is None else units
                td(units, cls=f'easyio_units')
        return container







