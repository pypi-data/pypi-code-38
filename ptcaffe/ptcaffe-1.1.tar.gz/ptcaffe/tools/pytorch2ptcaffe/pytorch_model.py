# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

import torch.onnx
import torchvision
from .onnx2ptcaffe import onnx2ptcaffe
from ptcaffe.utils.config import cfg

#from .onnx2ptcaffe import onnx2ptcaffe

def get_pytorch_model(model_name, verbose=False):

    dummy_input = torch.randn(10, 3, 224, 224)
    onnx_model_file = "%s.proto" % model_name
    pytorch_model = torchvision.models.__dict__[model_name](pretrained=True)
    pytorch_model.eval()
    print("export %s" % onnx_model_file)
    torch.onnx.export(pytorch_model, dummy_input, onnx_model_file, verbose=verbose)

    protofile = "%s.prototxt" % model_name
    weightfile = "%s.ptcmodel" % model_name
    onnx2ptcaffe(onnx_model_file, protofile, weightfile)

    # verify
    from ptcaffe.caffenet import CaffeNet
    ptcaffe_model = CaffeNet(protofile, phase='TEST')
    ptcaffe_model.load_model(weightfile)
    ptcaffe_model.set_automatic_outputs()
    ptcaffe_model.eval()

    input = torch.randn(10, 3, 224, 224)

    with torch.no_grad():
        pytorch_output = pytorch_model(input)
        ptcaffe_output = ptcaffe_model(input)
    diff = (pytorch_output - ptcaffe_output).data.abs().mean()
    print('difference between pytorch and ptcaffe: %f' % diff)

if __name__ == '__main__':
    from ptcaffe.utils.config import cfg
    get_pytorch_model('resnet50')
