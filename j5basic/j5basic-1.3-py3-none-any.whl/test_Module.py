#!/usr/bin/env python

import os
from j5basic import Module
from j5test import Utils

class TestModule:
    def test_find_module(self):
        target_file = Module.__file__
        if target_file.endswith(".pyc") or target_file.endswith(".pyo"):
            source_file = target_file[:target_file.rfind(".")] + ".py"
            if os.path.exists(source_file):
                target_file = source_file
        assert Module.find_module("j5basic") == os.path.dirname(target_file)
        assert Module.find_module("j5basic.Module") == target_file
        assert Utils.raises(ValueError, Module.find_module, "j5basic.NonExistent")

    def test_resolve(self):
        assert Module.resolvemodule("j5basic.Module") == Module
        # Run this twice to cover the cached usage
        assert Module.resolvemodule("j5basic.Module") == Module
        try:
            from j5.Config import ConfigTree
            assert Module.resolvemodule("j5.Config.ConfigTree.Node") == ConfigTree.Node
        except ImportError:
            pass

        assert Module.resolvemodule("j5basic.Module.canonicalize") == Module.canonicalize
        assert Utils.raises(ImportError, Module.resolvemodule, "j5basic.Moodle")

    class A(object):
        def mro_target1(self):
            print ("A")

        def mro_target3(self):
            print ("A")

    class B(object):
        def mro_target1(self):
            print ("B")

        def mro_target2(self):
            print ("B")

    class C(A):
        def mro_target2(self):
            print ("C")

    class D(B, C):
        def mro_target3(self):
            print ("D")

    def test_get_all_distinct_mro_targets(self):
        print (Module.get_all_distinct_mro_targets(self.D, 'mro_target1'))
        assert Module.get_all_distinct_mro_targets(self.D, 'mro_target1') ==\
            [self.B.mro_target1, self.A.mro_target1]

        assert Module.get_all_distinct_mro_targets(self.D, 'mro_target2') == \
               [self.B.mro_target2, self.C.mro_target2]
        assert Module.get_all_distinct_mro_targets(self.D, "mro_target3") == \
            [self.D.mro_target3]