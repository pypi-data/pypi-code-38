from qsa.ext.base import BaseExtension

from .schema import ConfigSchema


class Extension(BaseExtension):
    name = 'Quantum Specification'
    weight = -100.0

    def on_project_init(self, quantum, typname, name, *args, **kwargs):
        self.spec = {
            'version': "1"
        }
        quantum.update(self.spec)

