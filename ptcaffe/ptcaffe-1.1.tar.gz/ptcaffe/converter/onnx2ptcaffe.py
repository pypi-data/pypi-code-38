# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

import torch
from ptcaffe.tools.pytorch2ptcaffe.onnx2ptcaffe import onnx2ptcaffe
from ptcaffe.utils.config import cfg

def main():
    import sys
    if len(sys.argv) == 1:
        print('Usage: onnx2ptcaffe input_onnx output.prototxt output.ptcmodel')
        exit()
    elif len(sys.argv) == 4:
        input_onnx = sys.argv[1]
        output_protofile = sys.argv[2]
        output_ptcmodel = sys.argv[3]
        print('input_onnx = %s' % input_onnx)
        print('output_protofile = %s' % output_protofile)
        print('output_ptcmodel = %s' % output_ptcmodel)
        onnx2ptcaffe(input_onnx, output_protofile, output_ptcmodel)

if __name__ == '__main__':
    main()
