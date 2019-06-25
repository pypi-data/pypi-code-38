# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

import torch
from ptcaffe.caffenet import CaffeNet

def ptcaffe2onnx(input_protofile, input_ptcmodel, output_onnx):
    input_net = CaffeNet(input_protofile)
    input_net.load_model(input_ptcmodel)
    input_net.set_automatic_outputs()
    input_net.eval()
    input_shape = input_net.get_input_shapes()
    assert(not isinstance(input_shape[0], list))
    dummy_input = torch.randn(input_shape)
    torch.onnx.export(input_net, dummy_input, output_onnx, verbose=True)

def main():
    import sys
    if len(sys.argv) == 1:
        print('Usage: ptcaffe2onnx input.prototxt input.ptcmodel output.onnx')
        exit()
    elif len(sys.argv) == 4:
        input_protofile = sys.argv[1]
        input_ptcmodel = sys.argv[2]
        output_onnx = sys.argv[3]
        print('input_protofile = %s' % input_protofile)
        print('input_ptcmodel = %s' % input_ptcmodel)
        print('output_onnx = %s' % output_onnx)
        ptcaffe2onnx(input_protofile, input_ptcmodel, output_onnx)

if __name__ == '__main__':
    main()
