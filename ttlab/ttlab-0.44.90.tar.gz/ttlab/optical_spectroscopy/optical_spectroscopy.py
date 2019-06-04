from .cary5000 import Cary5000
from .insplorion import Insplorion
from .FDTD import FDTD

class OpticalSpectroscopy:

    def __init__(self, equipment_name, filename=None,gridfs=None):
        print('Hello')

    def __new__(cls, equipment_name, filename=None, gridfs=None, **kwargs):
        if equipment_name is EquipmentNames.cary5000:
            return Cary5000(filename=filename,gridfs=gridfs, **kwargs)
        elif equipment_name is EquipmentNames.insplorion:
            return Insplorion(filename)
        elif equipment_name is EquipmentNames.fdtdSimulation:
            return FDTD(filename_wavelength=kwargs['filename_wavelength'],filename_cross_section=kwargs['filename_cross_section'],simulation_names=kwargs['simulation_names'])
        else:
            raise NameError('Equipment name: ' + equipment_name + ' do not exist')

    @property
    def list_of_equipment_names(self):
        return [x for x in dir(EquipmentNames) if not x.startswith('__')]


class EquipmentNames:
    cary5000 = 'cary5000'
    insplorion = 'insplorion'
    fdtdSimulation = 'FDTD'
