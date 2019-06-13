# -*- coding: utf-8 -*-

import os
import shutil
import unittest

from pysp.sbasic import SFile
from pysp.serror import SDebug
from pysp.sconf import SYAML


main_yml = '''
main:
    cmd: main-command
    sublevel: !include sub_l1.yml
    tag: main
'''.strip()

sub_l1_yml = '''
cmd: sub-command
sublevel: !include sub_l2.yml
tag: sub level 1
'''.strip()

sub_l2_yml = '''
cmd: sub-command
sublevel: null
tag: sub level 2
'''.strip()

expected_mark_yml = '''
__include__:
    fullpath: /tmp/yaml/main.yml
    value: null
main:
    cmd: main-command
    sublevel:
        __include__:
            fullpath: /tmp/yaml/sub_l1.yml
            value: sub_l1.yml
        cmd: sub-command
        sublevel:
            __include__:
                fullpath: /tmp/yaml/sub_l2.yml
                value: sub_l2.yml
            cmd: sub-command
            sublevel: null
            tag: sub level 2
        tag: sub level 1
    tag: main
'''.strip()

merge_yml = '''
main:
    sublevel:
        sublevel:
            sublevel: Merge Point 1
merge: Merge Point 2
'''.strip()

expected_merge_yml = '''
__include__:
    fullpath: /tmp/yaml/main.yml
    value: null
main:
    cmd: main-command
    sublevel:
        __include__:
            fullpath: /tmp/yaml/sub_l1.yml
            value: sub_l1.yml
        cmd: sub-command
        sublevel:
            __include__:
                fullpath: /tmp/yaml/sub_l2.yml
                value: sub_l2.yml
            cmd: sub-command
            sublevel: Merge Point 1
            tag: sub level 2
        tag: sub level 1
    tag: main
merge: Merge Point 2
'''.strip()

yml_files = [main_yml, sub_l1_yml, sub_l2_yml]


def get_var_name(var, dir=locals()):
    return [key for key, val in dir.items() if id(val) == id(var)][0]


class YamlTest(unittest.TestCase, SDebug, SFile):
    # DEBUG = True
    folder = '/tmp/yaml/'

    def convert_filename(self, var):
        fname = get_var_name(var).split('_')
        return self.folder+'_'.join(fname[:-1])+'.'+fname[-1]

    def load_test(self, yaml):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        for item in yml_files:
            fpath = self.convert_filename(item)
            self.to_file(fpath, item)
        yfile = self.convert_filename(yml_files[0])
        self.ymlo = yaml.load(yfile)
        loaded_yml = yaml.dump(self.ymlo, pretty=True).strip()
        self.dprint(loaded_yml)
        self.assertTrue(loaded_yml == expected_mark_yml)

    def store_test(self, yaml):
        shutil.rmtree(self.folder)
        os.makedirs(self.folder)
        yaml.store(self.ymlo)

        for item in yml_files:
            fpath = self.convert_filename(item)
            data = self.read_all(fpath).strip()
            self.dprint('Load: {}'.format(fpath))
            self.assertTrue(data == item)

    def test_yaml(self):
        yaml = SYAML()
        self.load_test(yaml)
        self.store_test(yaml)

    def test_yaml_merge(self):
        yaml = SYAML()
        self.load_test(yaml)
        dy = self.ymlo
        uy = yaml.load(merge_yml)
        yo = yaml.merge(uy, dy)
        self.dprint(yaml.dump(yo, pretty=True))
        loaded_yml = yaml.dump(yo, pretty=True).strip()
        self.assertTrue(loaded_yml == expected_merge_yml)
