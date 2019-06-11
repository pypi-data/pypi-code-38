"""Interface for opening videos and getting frames using cv2.
"""
import cv2
import time

__version__ = '0.1'
__author__ = 'Rob Dupre (VCA)'


class OpenVideo:
    """Object to handle the CV2 interactions with opening a video file and getting frames
    """
    def __init__(self):
        # Open the video source
        self.width = 0
        self.height = 0
        self.fps = 0
        self.num_frames = 0
        self.vid = cv2.VideoCapture()
        self.frame_counter = -1

    def open_video(self, file_location):
        """Opens a video file and retrieves some metadata
        :param file_location: string of the video file location
        :return: bool success or fail
        """
        # OPEN THE VIDEO AT file_location
        try:
            self.vid = cv2.VideoCapture(file_location)
            self.frame_counter = -1
        except Exception as e:
            # IF THE VIDEO DID NOT OPEN RETURN FAIL
            print(e)
            raise ValueError("Unable to open video source {}".format(file_location))
            return False
        else:
            # Get video source width and height AND RETURN TRUE IF THAT THE FILE OPENED
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.fps = self.vid.get(cv2.CAP_PROP_FPS)
            self.num_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
            return True

    def open(self):
        """Returns if the Video stream is open, (mirrors cv2.VideoCapture.isOpened())
        :return: bool success or fail
        """
        return self.stream.isOpened()

    def get_frame(self):
        """Returns a frame from the open video
        :return: bool success or fail, cv2 frame or None
        """
        # CHECK THE VIDEO IS OPEN
        if self.vid.isOpened():
            # ATTEMPT TO READ THE FRAME
            ret, frame = self.vid.read()
            if ret:
                self.frame_counter = self.frame_counter + 1
                # Return a boolean success flag, and the current frame converted to BGR
                return ret, frame
                # return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                # RETURN FAIL CASE
                return ret, None
        else:
            # RETURN FAIL CASE
            return False, None

    def close_video(self):
        if self.vid.isOpened():
            self.vid.release()
            time.sleep(1)

    # Release the video source when the object's destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
