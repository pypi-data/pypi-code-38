import unittest
import numpy as np
import matplotlib.pyplot as plt
from pynoptes.dataloaders.vision import MOTDataset, MOT17DetDataset
from pynoptes.detection.boxes import width_height_to_coordinates
import cv2
import time


class TestDetection(unittest.TestCase):

    def test_bounding_box_conversion(self):
        mot_data = MOT17DetDataset(root_dir='/Users/fabianherzog/MOT17Det/')
        img = mot_data[50]['image']
        detections = mot_data[50]['detections']
        for det in detections:
            detection = width_height_to_coordinates(det)
            cv2.rectangle(img, (int(detection[0]), int(detection[1])),
                          (int(detection[2]), int(detection[3])),
                          (255, 0, 0), 2)
        plt.imshow(img)
        cv2.imwrite('test.png', img)
        plt.show()
