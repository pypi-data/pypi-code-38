import cv2
import threading
import time
import os

from microlab.io.folders import delete_folder, create_folder

class Camera:
    buffer = []

    def __init__(self, index=None):
        if index is None:
            print(' select vision index')
        else:
            self.index = index
        self.connected = False
        self.capture = False
        self.frame = None

    def connect(self):
        self.device = cv2.VideoCapture(self.index)
        self.connected = True
        print('vision connected')

    def disconnect(self):
        self.device.release()

    def get_frame(self):
        if self.connected:
            ret, frame = self.device.read()
            if ret:
                self.frame = frame
                self.capture = True
                self.buffer.append(frame)
                # self.write_frame()
            else:
                print('failed to get frame')

    def show_frame(self):
        if self.capture:
            cv2.imshow('{}'.format(self.frame.shape), self.frame)
            cv2.waitKey(0)

    def write_frame(self):
        cv2.imwrite('{}.jpg'.format(len(self.buffer)), self.frame)

    def start(self):
        self.thread = threading.Thread(target=self.record, args=())
        self.thread.daemon = True
        self.thread.start()
        print('start recording thread')

    def stop(self):
        if self.connected:
            self.connected=False
            print('vision stopped')
        time.sleep(0.2)

    def record(self):
        while self.connected:
            self.get_frame()

    def export(self, path, verbose=False):
        create_folder(path=path, verbose=verbose)
        for id, frame in enumerate(self.buffer):
            filename = os.path.join(path,'{}.jpg'.format(id))
            cv2.imwrite(filename=filename, img=frame)

    def clear(self, path, verbose=False):
        delete_folder(path, verbose=verbose)
