# rtsp_recorder.py
"""Simple fucntion to record the visualise and save the output of a RTSP stream
"""

import argparse
import cv2
from sys import exit
from rdutils.video_streamer import VideoStreamer

__version__ = '0.2'
__author__ = 'Rob Dupre (KU)'

parser = argparse.ArgumentParser(description='Config Tool to create settings files for each camera '
                                             'and the required algorithms.')
parser.add_argument('--file_location', default='test.avi',
                    type=str, help='The save location for the resultant settings file, also used as the input for '
                                   'frame analysers.')
parser.add_argument('--rtsp', default='rtsp://root:pass@10.144.129.107/axis-media/media.amp',
                    type=str, help='The RTSP stream address to allow access to the feed and run the config on.')
parser.add_argument('--framerate', default=25, type=int, help='The desired framerate at which the RTSP stream is '
                                                              'captured.')
_args = parser.parse_args()


def recorder(camera_address, fps, filename):

    cap = VideoStreamer(camera_address)
    cap.start()
    frame = cap.read()
    frame = cap.read()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, (frame.shape[1], frame.shape[0]))
    if cap.open():
        print("CAMERA CONNECTION ESTABLISHED. RECORDING STARTED")
        while cap.open():
            frame = cap.read()
            # frame.shape
            cv2.imshow('frame', frame)
            out.write(frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                out.release()
                break
    else:
        print("FAILED TO CONNECT TO CAMERA.")
        exit(-1)


if __name__ == '__main__':
    print(_args.rtsp)
    print(_args.file_location)
    print(_args.framerate)
    recorder(_args.rtsp, _args.framerate, _args.file_location)
