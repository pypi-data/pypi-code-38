from pyrediseasyio.io.base import SingleIO
from dominate.tags import div, tr, td



class HTMLIO:

    def __init__(self, io: SingleIO, html_id_header: str, namespace: str = 'pyredeio'):
        self.io = io
        self.namespace = namespace
        self.html_id_header = html_id_header

    @staticmethod
    def html_id_for(header: str, attr: SingleIO):
        return f'{header}_{attr.addr}_io'

    @property
    def html_id(self):
        return self.html_id_for(self.html_id_header, self.io)

    @property
    def html_class(self):
        return f'{self.namespace}_io'

    def html(self, show_units: bool = True):
        io = self.io
        name, addr, val, units = io.name, io.addr, io.value, io.units
        with div(cls=self.html_class, id=self.html_id) as container:
            div(name, cls=f'{self.html_class}_name')
            div(val, cls=f'{self.html_class}_value', id=f'{self.html_id}_value', onchange='OnIOValueChange(event)')
            if show_units:
                units = '' if units is None else units
                div(units, cls=f'{self.html_class}_units')
        return container

    def html_row(self, show_units: bool = True):
        io = self.io
        name, addr, val, units = io.name, io.addr, io.value, io.units
        with tr(cls=self.html_class, id=self.html_id) as container:
            td(name, cls=f'{self.html_class}_name')
            td(val, cls=f'{self.html_class}_value', id=f'{self.html_id}_value', onchange='OnIOValueChange(event)')
            if show_units:
                units = '' if units is None else units
                td(units, cls=f'{self.html_class}_units')
        return container







