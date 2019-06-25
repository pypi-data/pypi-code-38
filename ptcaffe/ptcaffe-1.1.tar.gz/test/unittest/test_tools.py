import unittest
from ptcaffe.caffenet import CaffeNet
import os

def setUp():
    protofile = './test/unittest/deploy.prototxt'
    ptcmodel = './test/unittest/pelee.ptcmodel'
    net = CaffeNet(protofile)
    net.save_model(ptcmodel)

def teardown():
    os.remove('./test/unittest/pelee.ptcmodel')

class TestBnTools(unittest.TestCase):
    def test_MergeScale(self):
        print('ToolsTest: merge scale')
        from ptcaffe.tools.merge_scale import merge_scale
        
        input_protofile = './test/unittest/deploy.prototxt'
        input_ptcmodel = './test/unittest/pelee.ptcmodel'
        output_protofile = './test/unittest/deploy.noscale.prototxt'
        output_ptcmodel = './test/unittest/pelee_noscale.ptcmodel'
        merge_scale(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)

    def test_SplitScale(self):
        print('ToolsTest: split scale')
        from ptcaffe.tools.split_scale import split_scale
        input_protofile = './test/unittest/deploy.noscale.prototxt'
        input_ptcmodel = './test/unittest/pelee_noscale.ptcmodel'
        output_protofile = './test/unittest/peleenet_deploy.prototxt'
        output_ptcmodel = './test/unittest/peleenet.ptcmodel'
        split_scale(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)
        os.remove(input_protofile)
        os.remove(input_ptcmodel)
        os.remove(output_protofile)
        os.remove(output_ptcmodel)

    def test_MergeBn(self):
        print('ToolsTest: merge bn')
        from ptcaffe.tools.merge_bn import merge_bn
        input_protofile = './test/unittest/deploy.prototxt'
        input_ptcmodel = './test/unittest/pelee.ptcmodel'
        output_protofile = './test/unittest/peleenet_deploy.nobn.prototxt'
        output_ptcmodel = './test/unittest/peleenet_nobn.ptcmodel'
        merge_bn(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)
        os.remove(output_protofile)
        os.remove(output_ptcmodel)

