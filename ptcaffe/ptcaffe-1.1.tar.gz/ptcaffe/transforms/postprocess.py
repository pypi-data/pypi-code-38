class PrintResult:
    def __call__(self, result):
        for key,value in result.items():
            print('%s: %s' % (key, str(value)))
        return result

class PrintSSDDetection:
    def __init__(self, classes):
        self.classes = classes

    def __call__(self, result, infile, outfile):
        img = cv2.imread(infile)
        detection_output = result.squeeze(0).squeeze(0)
        for i in range(detection_output.shape[0]):
            predict = detection_output[i]
            img_id = predict[0]
            label  = self.classes[int(predict[1])]
            score  = predict[2]
            bbox   = predict[3:]
            x1     = bbox[0] * img.shape[1]
            y1     = bbox[1] * img.shape[0]
            x2     = bbox[2] * img.shape[1]
            y2     = bbox[3] * img.shape[0]

            x1     = int(min(max(round(x1), 0), img.shape[1]))
            y1     = int(min(max(round(y1), 0), img.shape[0]))
            x2     = int(min(max(round(x2), 0), img.shape[1]))
            y2     = int(min(max(round(y2), 0), img.shape[0]))
            #cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            text = "%d" % i
            print("%d: %s %0.3f [%d, %d, %d, %d]" % (i, label, score, x1, y1, x2, y2))

        return result, infile, outfile
