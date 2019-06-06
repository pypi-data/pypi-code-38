import numpy as np
import os
import cv2
from mvnc import mvncapi as mvnc

class FaceEmbedderMovidiusFacenet:

    def __init__(self, movidius_id=0):

        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Get a list of ALL the sticks that are plugged in
        # we need at least one
        devices = mvnc.EnumerateDevices()
        if len(devices) < movidius_id+1:
            print('Not enough devices found')
            quit()

        # Pick the first stick to run the network
        self.device = mvnc.Device(devices[movidius_id])

        # Open the NCS
        self.device.OpenDevice()

        # Read in the graph file to memory buffer
        graphfile = dir_path + "/model/20170512-110547_mvds/facenet_movidius_ncs.graph"
        with open(graphfile, mode='rb') as f:
            graph_in_memory = f.read()

        # create the NCAPI graph instance from the memory buffer containing the graph file.
        self.graph = self.device.AllocateGraph(graph_in_memory)

    def close(self):

        self.graph.DeallocateGraph()
        self.device.CloseDevice()

    def _whiten_image(self, source_image):

        source_mean = np.mean(source_image)
        source_standard_deviation = np.std(source_image)
        std_adjusted = np.maximum(source_standard_deviation, 1.0 / np.sqrt(source_image.size))
        whitened_image = np.multiply(np.subtract(source_image, source_mean), 1 / std_adjusted)
        return whitened_image

    def _load_image(self, image_path):

        img = cv2.imread(os.path.expanduser(image_path))
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def _scale_image(self, image):

        NETWORK_WIDTH = 160
        NETWORK_HEIGHT = 160
        return cv2.resize(image, (NETWORK_WIDTH, NETWORK_HEIGHT))

    def get_embedding(self, image_path):

        # Load image
        image = self._load_image(image_path)

        return self.get_embedding_mem(image)

    def get_embedding_mem(self, cv_image):

        # Scale image
        image = self._scale_image(cv_image)

        # Whiten image
        image = self._whiten_image(image)

        # Send images to NCS
        self.graph.LoadTensor(image.astype(np.float16), None)

        # Get results from NCS
        output, userobj = self.graph.GetResult()

        return output





