# video_streamer.py
"""Implementation of an RTSP or Video stream reader utilising OpenCV"""
import cv2
import numpy as np
from threading import Thread
import time

__version__ = '0.2'
__author__ = 'Rob Dupre (KU)'


class VideoStreamer:
    def __init__(self, cam_file_path, frame_size=(None, None), identifier=1, threaded=True):
        """Opens a video file
        :param cam_file_path: string of the video file location or RTSP Stream address (with authentication)
        :param frame_size: (OPTIONAL) When present will resize to the frame_size the loaded frames
        :param identifier: (OPTIONAL) id for this stream
        :param threaded: (OPTIONAL) bool determining if the video should stream in a sperate thread
        """
        self.stream = cv2.VideoCapture(cam_file_path)
        self.id = identifier
        self.threaded = threaded
        self.fps = 0
        if self.open():
            print('CONNECTION ESTABLISHED.')
            self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        else:
            print('FAILED TO LOAD MEDIA ' + str(self.id) + '.')

        self.stopped = False
        self.size = frame_size
        self.current_frame = np.zeros([800, 200, 3])
        self.grabbed = False

    def open(self):
        """Returns if the Video stream is open, (mirrors cv2.VideoCapture.isOpened())
        :return: bool success or fail
        """
        return self.stream.isOpened()

    def start(self):
        """Sets self.stopped to False and if threaded creates thread to handle the update() function
        :return: self
        """
        if self.threaded:
            t = Thread(target=self._update, args=())
            t.daemon = True
            t.start()
            # ADD DELAY TO ALLOW STREAMER TO BUFFER SOME INITIAL FRAMES
            time.sleep(0.5)
        self.stopped = False
        return self

    def _update(self):
        """Updates the self.current_frame with the latest frame from the streamer object and the self.grabbed bool
        will close the thread if the stream fails.
        """
        while True:
            if self.stopped:
                return

            self._read_frame()

            if not self.grabbed:
                self.stop()
                return

    def read(self):
        """Reads the most recent frame into self.current_frame, for use when not threaded
        """
        if not self.threaded:
            self._read_frame()

            if not self.grabbed:
                self.stop()

        return self.current_frame

    def stop(self):
        """Sets the self.stopped bool to True but doesn't close the thread, stopping the reading of frames
        """
        self.stopped = True

    def save(self, filename):
        """Saves the current frame to a png file
        :param filename: string filename to save the image
        """
        print('Screen shot Saved')
        cv2.imwrite(filename + '.png', self.current_frame)

    def _read_frame(self):
        """Gets the most recent frame and if a specific size has been specified will resize the frame accordingly
        """
        self.grabbed, image = self.stream.read()
        if self.size[0] is None:
            self.current_frame = image
        else:
            self.current_frame = cv2.resize(image, self.size)


# cap1 = CamVideoStreamer('rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov')
# cap1.start()
# while True:
#     # frame1 = cap1.read()
#     frame1 = cap1.read_last()
#     # frame1 = cap1.current_frame
#     cv2.imshow('Video', frame1)
#     if cv2.waitKey(1) == ord('c'):
#         exit(0)
