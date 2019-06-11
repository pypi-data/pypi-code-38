# image_sequence_streamer.py
""" Loads an Image sequence and returns each frame sequentially when called. Provides options for looping the stream or
repeating the last frame"""
import cv2
import os

__version__ = '0.2'
__author__ = 'Rob Dupre (KU)'


class ImageSequenceStreamer:
    def __init__(self, seq_path, start_frame=0, frame_size=None, loop_last=True, repeat=False):
        """Loads an Image sequence and returns each frame sequentially when called. Provides options for looping the
        stream or repeating the last frame
        :param seq_path: String identifying the folder location of the images.
        :param start_frame: [OPTIONAL] Allows for the image sequence to start at a specific point
        :param frame_size: [OPTIONAL] Allows for loaded frames to be resized
        :param loop_last: [OPTIONAL] if True last frame is repeated until stop is called
        :param repeat: [OPTIONAL] if True repeats all frames until stop is called
        """
        self.folder_location = seq_path
        self.file_list = []
        self.images = []
        self.start_frame = start_frame
        self.image_count = self.start_frame
        self.current_image = []
        self.working = False
        self.loop_last = loop_last
        self.repeat = repeat

        # GET LIST OF IMAGES AT FILE LOCATION
        valid_images = ('.jpg', '.png', '.tga', '.tif', '.jpeg')
        for f in sorted(os.listdir(self.folder_location)):
            ext = os.path.splitext(f)[1]
            if ext.lower().endswith(valid_images):
                self.file_list.append(os.path.join(self.folder_location, f))

        # GET THE FRAME SIZE FROM THE FIRST IMAGE IF NOT SPECIFIED
        if frame_size[0] is None:
            temp_image = cv2.imread(self.file_list[self.image_count])
            if temp_image.shape[0] > temp_image.shape[1]:
                self.size = (temp_image.shape[0], temp_image.shape[1])
            else:
                self.size = (temp_image.shape[1], temp_image.shape[0])
        else:
            self.size = (frame_size[0], frame_size[1])

        # IF WORKING THE STREAMER WILL ALLOW THE RETURN OF THE NEXT IMAGE. IF NOT THE STREAM IS CONSIDERED stopped
        if len(self.file_list) > 0:
            self.working = True
            print('IMAGE SEQUENCE FOUND AND LOADED.')
        else:
            self.working = False
            print('NO IMAGES FOUND.')

    def open(self):
        """Returns if the Image Sequence stream is open
        :return: bool success or fail
        """
        return self.working

    def start(self):
        """Sets the self.working bool to True starting the cycle of frames
        """
        self.working = True

    def stop(self):
        """Sets the self.working bool to False stopping the cycle of frames
        """
        self.working = False

    def read(self):
        """Returns the most recently read frame
        :return: image
        """
        # LOAD THE NEXT IMAGE AS LONG AS THERE ARE STILL ENTRIES IN THE file_list,
        if self.image_count < len(self.file_list) - 1:
            self.current_image = cv2.resize(cv2.imread(self.file_list[self.image_count]), self.size)
            # self.current_image = self.images[self.image_count]
            self.image_count = self.image_count + 1
        # THIS IS NOW THE LAST IMAGE IN THE LIST
        elif self.image_count == len(self.file_list) - 1:
            self.current_image = cv2.resize(cv2.imread(self.file_list[self.image_count]), self.size)
            if self.repeat:
                self.image_count = self.start_frame
            else:
                self.image_count = self.image_count + 1
            # ELSE: IF NOT loop_last RETURN BLANK FRAME AND STOP OR LEAVE self.current_image AS THE LAST IMAGE LOADED
            if not self.loop_last and not self.repeat:
                self.working = False
        # NOW IN INFINITE LOOP AS current_image WILL ONLY EVER HOLD THE LAST IMAGE.

        return self.current_image

    def save(self, filename):
        print('Screen shot Saved')
        cv2.imwrite(filename + '.png', self.current_image)
