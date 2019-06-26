import cv2
import numpy as np
from queue import Queue
import _thread


class YOLOv3:
    def __init__(self, classesFile, modelConfiguration, modelWeights):
        # Initialize the parameters
        self.confThreshold = 0.5  #Confidence threshold
        self.nmsThreshold = 0.4   #Non-maximum suppression threshold
        self.inpWidth = 416       #Width of network's input image
        self.inpHeight = 416      #Height of network's input image
        self.inputQueue = Queue(maxsize=1)
        self.outputQueue = Queue(maxsize=1)
        self.outs = None

        # Load names of classes
        self.classes = None
        with open(classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

        self.net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        _thread.start_new_thread(self.process_frame, ())

    # Get the names of the output layers
    def getOutputsNames(self):
        # Get the names of all the layers in the network
        layersNames = self.net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    # Remove the bounding boxes with low confidence using non-maxima suppression
    def detect(self, frame, draw=True):
        detected = []
        if self.inputQueue.empty():
            self.inputQueue.put(frame)

        outs = self.outs
        if not self.outputQueue.empty():
            outs = self.outputQueue.get()
            self.outs = outs
        if outs is None:
            outs = self.outs
        if outs is None:
            return detected

        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        classIds = []
        confidences = []
        boxes = []
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)

        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]

            label = '%.2f' % confidences[i]
            if self.classes:
                assert (classIds[i] < len(self.classes))
                label = '%s:%s' % (self.classes[classIds[i]], label)
            if draw:
                self.draw_label(frame, label, left, top, width, height)
            detected.append((label, left, top, width, height))
        return detected


    def draw_label(self, frame, label, left, top, width, height):
        cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 0, 255), 2)
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


    def process_frame(self):
        while True:
            if not self.inputQueue.empty():
                frame = self.inputQueue.get()
                blob = cv2.dnn.blobFromImage(frame, 1 / 255, (self.inpWidth, self.inpHeight), [0, 0, 0], 1, crop=False)
                self.net.setInput(blob)
                detections = self.net.forward(self.getOutputsNames())
                self.outputQueue.put(detections)
