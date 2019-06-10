import os, sys

import numpy as np
import matplotlib.pyplot as plt
from cv2 import VideoWriter, imread, resize
import cv2

class BaseEnv(object):
    def make_world(self):
        raise NotImplementedError

    def reset_world(self):
        raise NotImplementedError

    def convert_image(self):
        raise NotImplementedError

    def plot_map_cv2(self, resize_width=1000, resize_height=1000):
        img = cv2.resize(self.convert_img(), (resize_width,resize_height),
                         interpolation=cv2.INTER_AREA)
        cv2.imshow("World2", img)

    def plot_map(self):
        plt.figure(figsize=(10, 10))
        img = self.convert_img()
        plt.imshow(img, interpolation="nearest")
        #plt.imshow(self._layout > -1, interpolation="nearest")
        ax = plt.gca()
        ax.grid(0)
        plt.xticks([])
        plt.yticks([])
        h, w = self.h, self.w
        for y in range(h-1):
            plt.plot([-0.5, w-0.5], [y+0.5, y+0.5], '-k', lw=2)
        for x in range(w-1):
            plt.plot([x+0.5, x+0.5], [-0.5, h-0.5], '-k', lw=2)

    def make_video(self, images, outvid=None, fps=5, size=None, is_color=True, format="XVID"):
        """
        Create a video from a list of images.
        @param      outvid      output video
        @param      images      list of images to use in the video
        @param      fps         frame per second
        @param      size        size of each frame
        @param      is_color    color
        @param      format      see http://www.fourcc.org/codecs.php
        """
        # fourcc = VideoWriter_fourcc(*format)
        # For opencv2 and opencv3:
        if int(cv2.__version__[0]) > 2:
            fourcc = cv2.VideoWriter_fourcc(*format)
        else:
            fourcc = cv2.cv.CV_FOURCC(*format)
        vid = None
        for image in images:
            assert os.path.exists(image)
            img = imread(image)
            if vid is None:
                if size is None:
                    size = img.shape[1], img.shape[0]
                vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)
            if size[0] != img.shape[1] and size[1] != img.shape[0]:
                img = resize(img, size)
            vid.write(img)
        vid.release()
