
import shutil
import unittest

from pysp.sbasic import SFile
from pysp.serror import SDebug
from pysp.sconf import SConfig


class Expected:
    default_vehicle = '''
car:
    sedan:
        SM6:
            transmission: cvt
    suv:
        QM6:
            transmission: cvt
'''.strip()

    user_vehicle = '''
car:
    suv:
        QM6:
            color: cloud-perl
            transmission: CVT
'''.strip()

    overlay_user_vehicle = '''
car:
    sedan:
        SM6:
            transmission: cvt
    suv:
        QM6:
            color: cloud-perl
            transmission: CVT
'''.strip()


class FolderConfig:
    root = '''
car:
    sedan: !include folder/sedan
    suv: !include folder/suv

'''.strip()

    car_sedan = '''
SM6:
    transmission: cvt
'''.strip()

    car_suv = '''
QM6:
    transmission: cvt
'''.strip()


class ConfigList:
    target = '''
car:
    sedan:
      - name: SM6
        vendor: renault
      - name: Avante
        vendor: Hyundae
      - name: K7
        vendor: KIA
      - name: Others
        vendor:
          - Ford
          - BMW
          - Audi
'''.strip()


class ConfigTest(unittest.TestCase, SDebug, SFile):
    # DEBUG = True
    def_folder = '/tmp/yaml/default/'
    user_folder = '/tmp/yaml/user/'

    def config_create_default(self):
        cfg = SConfig()
        cfg.set_value('car.suv.QM6.transmission', 'cvt')
        cfg.set_value('car.sedan.SM6.transmission', 'cvt')
        cfgfile = self.def_folder+'vehicle'
        cfg.store(cfgfile)
        load_vehicle = self.read_all(cfgfile).strip()
        self.assertTrue(Expected.default_vehicle == load_vehicle)

    def config_create_user(self):
        cfg = SConfig()
        cfg.set_value('car.suv.QM6.transmission', 'CVT')
        cfg.set_value('car.suv.QM6.color', 'cloud-perl')
        cfgfile = self.user_folder+'vehicle'
        cfg.store(cfgfile)
        load_vehicle = self.read_all(cfgfile).strip()
        self.assertTrue(Expected.user_vehicle == load_vehicle)

    def config_merge(self):
        cfg = SConfig(self.def_folder+'vehicle')
        cfg.collecting(self.user_folder+'vehicle')
        cfg.store()
        cfgfile = self.user_folder+'vehicle'
        load_vehicle = self.read_all(cfgfile).strip()
        self.assertTrue(Expected.overlay_user_vehicle == load_vehicle)

    def test_config(self):
        self.config_create_default()
        self.config_create_user()
        self.config_merge()

    def test_config_folder(self):
        shutil.rmtree(self.def_folder)
        shutil.rmtree(self.user_folder)
        self.to_file(self.def_folder+'vehicle', FolderConfig.root)
        self.to_file(self.def_folder+'/folder/sedan', FolderConfig.car_sedan)
        self.to_file(self.def_folder+'/folder/suv', FolderConfig.car_suv)
        cfg = SConfig(self.def_folder+'vehicle')
        # self.DEBUG = True
        self.dprint('\n'+cfg.dump())
        cfg.collecting(self.user_folder+'vehicle')
        self.dprint('\n'+cfg.dump())
        cfg.store()
        cfg2 = SConfig(self.user_folder+'vehicle')
        self.dprint('\n'+cfg.dump())
        self.dprint('\n'+cfg2.dump())
        self.assertTrue(cfg.dump() == cfg2.dump())
        for fname in ['vehicle', 'folder/sedan', 'folder/suv']:
            default_load = self.read_all(self.def_folder+fname).strip()
            user_load = self.read_all(self.user_folder+fname).strip()
            self.assertTrue(default_load == user_load)

    def test_access_keylist(self):
        cfgfile = '/tmp/yaml2/config_list.yml'
        self.to_file(cfgfile, ConfigList.target)
        cfg = SConfig(cfgfile)
        self.assertTrue(cfg.get_value('car.sedan[2].name') == 'K7')
        self.assertTrue(cfg.get_value('car.sedan[1].vendor') == 'Hyundae')
        self.assertTrue(cfg.get_value('car.sedan[0].name') == 'SM6')
        self.assertTrue(cfg.get_value('car.sedan[-2].name') == 'K7')
        self.assertTrue(cfg.get_value('car.sedan[100].name', 'NA') == 'NA')
        self.assertTrue(cfg.get_value('car.sedan[-1].vendor[1]') == 'BMW')
        cfg.set_value('car.sedan[-1].name', 'Overseas')
        self.assertTrue(cfg.get_value('car.sedan[-1].name') == 'Overseas')
        cfg.set_value('car.sedan[-1].vendor[-1]', 'Benz')
        self.assertTrue(cfg.get_value('car.sedan[-1].vendor[-1]') == 'Benz')
        # Append value to list, but it allows only the index is the next number
        cfg.set_value('car.sedan[-1].vendor[3]', 'Audi')
        self.assertTrue(cfg.get_value('car.sedan[-1].vendor[-1]') == 'Audi')
        cfg.set_value('car.suv[0]', 'QM6')
        cfg.set_value('car.suv[1]', 'Tusan')
        cfg.set_value('car.suv[2]', 'Tivoli')
        self.assertTrue(cfg.get_value('car.suv[-1]') == 'Tivoli')

        cfg.delete('car.suv[1]')
        self.assertTrue(cfg.get_value('car.suv[1]') == 'Tivoli')
        cfg.delete('car.sedan[-1].vendor[-1]')
        self.assertTrue(cfg.get_value('car.sedan[-1].vendor[-1]') == 'Benz')
        cfg.set_value('car.suv', None)
        self.assertTrue(cfg.get_value('car.suv') is None)
        cfg.delete('car.suv')
        self.assertTrue(cfg.get_value('car.suv', 'Nothing') == 'Nothing')
        cfg.delete('car.sedan[-1].vendor')
        result = cfg.get_value('car.sedan[-1].vendor', 'Nothing')
        self.assertTrue(result == 'Nothing')
        cfg.store()
