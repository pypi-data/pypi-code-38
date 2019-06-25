import cv2
import torch

from collections import OrderedDict
from ptcaffe.utils.logger import logger

from .base_server import BaseServer

from flask import request

class SegmentationServer(BaseServer):
    def __init__(self, protofile, weightfile, device):
        super(SegmentationServer, self).__init__(protofile, weightfile, device)

        server_param = self.net.net_info.get('server', OrderedDict())
        segmentation_param = server_param.get('segmentation_param', OrderedDict())

        if 'classes_file' in segmentation_param:
            self.classes = load_classes(segmentation_param['classes_file'])
        elif 'classes' in segmentation_param:
            self.classes = segmentation_param['classes'].split(',')
        else:
            self.classes = None
            logger.warning("classes or classes_file is needed in segmentation_param")

        colormap = [[0,0,0],[128,0,0],[0,128,0], [128,128,0], [0,0,128],
                    [128,0,128],[0,128,128],[128,128,128],[64,0,0],[192,0,0],
                    [64,128,0],[192,128,0],[64,0,128],[192,0,128],
                    [64,128,128],[192,128,128],[0,64,0],[128,64,0],
                    [0,192,0],[128,192,0],[0,64,128]]

        self.color_map = torch.ByteTensor(colormap)

    def inference(self):
        eval_outputs = self.net.eval_outputs
        if len(eval_outputs) != 1:
            return "Only one output is allowed, the output is score value range 0~1"

        if request.method == 'GET':
            imgfile = request.args.get('filename')
            result = self.forward(imgfile) 

            img = cv2.imread(imgfile)
            width = img.shape[1]
            height = img.shape[0]

            score_map = result
            output_str = "score_map.shape: %s" % str(score_map.shape)
            max_vals, max_idxs = score_map.max(1, keepdim=True)
            
            color_img = idx2rgb(max_idxs.cpu(), self.color_map)
            cv2.imwrite(imgfile+"_seg.jpg", color_img)
            orig_img = cv2.imread(imgfile)
            mask = (max_idxs > 0).view(height, width, 1).expand(height, width, 3)
            merge_img = merge_seg(orig_img, color_img, mask)
            cv2.imwrite(imgfile+"_merge.jpg", merge_img)
            
            output_str = '<img src="%s"></img> <p> <img src="%s"></img> <p> <img src="%s"></img> ' % (imgfile, imgfile+"_seg.jpg", imgfile+"_merge.jpg")
            

        elif request.method == 'POST':
            buffer = six.BytesIO(request.get_data())
            result = self.forward(buffer) 

            if len(eval_outputs) == 1: result = [result]
    
            output = dict()
            for idx, name in enumerate(eval_outputs):
                output[name] = result[idx].cpu().tolist()
            output_str = jsonify(output)

        return output_str


def idx2rgb(idx_img, color_map):
    width = idx_img.shape[3]
    height = idx_img.shape[2]
    color_img = color_map.index_select(0, idx_img.view(-1).long())
    color_img = color_img.view(height, width, 3)
    return color_img.numpy()

def merge_seg(orig_img, seg_img, mask):
    orig_img = torch.from_numpy(orig_img).float()
    seg_img = torch.from_numpy(seg_img).float()
    orig_img[mask] = orig_img[mask] * 0.3 + seg_img[mask] * 0.7
    orig_img = orig_img.byte().numpy()
    return orig_img
    
