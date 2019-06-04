#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from mvnc import mvncapi as mvnc


class FaceDetectorMovidiusSSD:

    def __init__(self, movidius_id=0, longrange=False):

        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/model"

        # Define constants
        self.NETWORK_INPUT_SIZE = 300
        self.NETWORK_OUTPUT_SIZE = 707

        # Get Movidius Devices
        devices = mvnc.EnumerateDevices()
        if len(devices) < movidius_id+1:
            print('Not enough devices found')
            quit()

        # Load SSD Graph
        if longrange:
            graphfile = dir_path + "/ssd_longrange.graph"
        else:
            graphfile = dir_path + "/ssd.graph"
        with open(graphfile, mode='rb') as rf:
            graphfile = rf.read()

        self.SSDGraphDevice = mvnc.Device(devices[movidius_id])
        self.SSDGraphDevice.OpenDevice()

        self.SSDGraph = self.SSDGraphDevice.AllocateGraph(graphfile)

    def close(self):

        self.SSDGraph.DeallocateGraph()
        self.SSDGraphDevice.CloseDevice()

    def detect_face_image(self, img):
        img_height, img_width, img_channels = img.shape
        img = cv2.resize(img, (self.NETWORK_INPUT_SIZE, self.NETWORK_INPUT_SIZE))
        img = img - 127.5
        img = img / 127.5
        img = img.astype(np.float16)

        self.SSDGraph.LoadTensor(img, None)
        out, userobj = self.SSDGraph.GetResult()
        out = out.tolist()

        probs, boxes = self._get_detection_boxes(out, img_width, img_height, 0.2)

        return boxes

    def detect_face(self, imgpath):

        img = cv2.imread(imgpath)
        return self.detect_face_image(img)

    def _get_detection_boxes(self, predictions, w, h, thresh):
        num = predictions[0]
        score = 0
        cls = 0

        probs = []
        boxes = []
        for i in range(1, int(num)+1):
            score = predictions[i*7+2]
            cls = predictions[i*7+1]
            if score > thresh and cls <= 1:
                probs.append(score)
                x1 = int(predictions[i*7+3]*w)
                y1 = int(predictions[i*7+4]*h)
                x2 = int(predictions[i*7+5]*w)
                y2 = int(predictions[i*7+6]*h)
                box = [x1, y1, x2, y2]
                boxes.append(box)
        return probs, boxes

