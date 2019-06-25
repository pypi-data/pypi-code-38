import cv2
from collections import OrderedDict
from ptcaffe.utils.logger import logger

from .base_server import BaseServer
from .classification import load_classes

from flask import request

class DetectionServer(BaseServer):
    def __init__(self, protofile, weightfile, device):
        super(DetectionServer, self).__init__(protofile, weightfile, device)

        server_param = self.net.net_info.get('server', OrderedDict())
        detection_param = server_param.get('detection_param', OrderedDict())

        if 'classes_file' in detection_param:
            self.classes = load_classes(detection_param['classes_file'])
        elif 'classes' in detection_param:
            self.classes = detection_param['classes'].split(',')
        else:
            self.classes = None
            logger.warning("classes or classes_file is needed in detection_param")

    def inference(self):
        eval_outputs = self.net.eval_outputs
        if len(eval_outputs) != 1:
            return "Only one output is allowed, the output should from DetectionOutput or YoloDetectionOutput"

        if request.method == 'GET':
            imgfile = request.args.get('filename')
            result = self.forward(imgfile) 

            output_html = "" #"%s: %s" % (eval_outputs[0], result.cpu().tolist())

            img = cv2.imread(imgfile)
            detection_output = result.squeeze(0).squeeze(0)
            print('detection_output.shape = ', detection_output.shape)
            for i in range(detection_output.shape[0]):
                predict = detection_output[i]
                img_id = predict[0]
                label  = self.classes[int(predict[1])]
                score  = predict[2]
                bbox   = predict[3:]
                x1     = float(bbox[0]) * img.shape[1]
                y1     = float(bbox[1]) * img.shape[0]
                x2     = float(bbox[2]) * img.shape[1]
                y2     = float(bbox[3]) * img.shape[0]

                x1     = int(min(max(round(x1), 0), img.shape[1]))
                y1     = int(min(max(round(y1), 0), img.shape[0]))
                x2     = int(min(max(round(x2), 0), img.shape[1]))
                y2     = int(min(max(round(y2), 0), img.shape[0]))
                cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
                #text = "%s:%0.3f" % (label, score)
                text = "%d" % i
                output_html = "%s <p> %d: %s %0.3f [%d, %d, %d, %d]" % (output_html, i, label, score, x1, y1, x2, y2)
                cv2.putText(img, text, (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            cv2.imwrite(imgfile + "_det.jpg", img)
            output_html = ' <img src="%s"></img> <p> %s' % (imgfile+"_det.jpg", output_html)

        elif request.method == 'POST':
            buffer = six.BytesIO(request.get_data())
            result = self.forward(buffer) 

            if len(eval_outputs) == 1: result = [result]
    
            output = dict()
            for idx, name in enumerate(eval_outputs):
                output[name] = result[idx].cpu().tolist()
            output_html = jsonify(output)

        return output_html

    def labeling(self):
        return "not supported"
