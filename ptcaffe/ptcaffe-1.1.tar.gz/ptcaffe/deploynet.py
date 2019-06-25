from __future__ import division, print_function

from ptcaffe.utils.logger import logger
from ptcaffe.caffenet import CaffeNet
from ptcaffe.transforms import create_transform

class DeployNet:
    def __init__(self, protofile, weightfile, device):
        net = CaffeNet(protofile, phase='TEST')
        self.device = device

        # GPU
        if device:
            if device.find(',') == -1:
                logger.info('single gpu device %s' % device)
                device_id = int(device)
                net.cuda(device_id)
                net.broadcast_device_ids([device_id])
            else:
                device_ids = device.split(',')
                logger.info('multi gpu devices %s' % device)
                device_ids = [int(i) for i in device_ids]
                net = ParallelCaffeNet(net.cuda(device_ids[0]), device_ids=device_ids)

        self.net = net
        self.net.load_model(weightfile)

        net_info = net.net_info
        deploy_param = net_info['props']['deploy']
        preprocess_param = deploy_param['preprocess_param']
        postprocess_param = deploy_param['postprocess_param']

        self.preprocess     = create_transform(preprocess_param)
        self.postprocess    = create_transform(postprocess_param)

    def __call__(self, infile, outfile):
        data = self.preprocess(infile)
        if self.device:
            data = data.cuda()

        result = dict()
        outputs = self.net(data)
        eval_outputs = self.net.eval_outputs
        if len(eval_outputs) == 1:
            result[eval_outputs[0]] = outputs
        elif len(eval_outputs) > 1:
            for idx, name in enumerate(eval_outputs):
                result[name] = outputs[idx].cpu()
 
        return self.postprocess(result, infile, outfile)
