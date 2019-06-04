#!python

import sys
import cv2
import time
import yaml
from big_fiubrother_detection.face_detector_thread import FaceDetectorThread
from big_fiubrother_detection.face_detector_factory import FaceDetectorFactory


def drawBoxes(im, boxes, color):
    x1 = [i[0] for i in boxes]
    y1 = [i[1] for i in boxes]
    x2 = [i[2] for i in boxes]
    y2 = [i[3] for i in boxes]
    for i in range(len(boxes)):
        cv2.rectangle(im, (int(x1[i]), int(y1[i])), (int(x2[i]), int(y2[i])), color, 1)
    return im


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("--------------------------------")
        print("This script receives a face detectory type and displays a webcam feed with overlaid face detection.")
        print("Press 'q' to quit.")
        print("")
        print("Usage: ")
        print("python demo_webcam.py ['mvds_ssd' | 'mvds_ssd_longrange' | 'mvds_mtcnn' | 'caffe_mtcnn']")
        print("--------------------------------")

    else:

        # Create Face Detector
        face_detector_type = sys.argv[1]
        if face_detector_type == "mvds_ssd":
            faceDetectorObject = FaceDetectorFactory.build_movidius_ssd()
        elif face_detector_type == "mvds_ssd_longrange":
            faceDetectorObject = FaceDetectorFactory.build_movidius_ssd_longrange()
        elif face_detector_type == "mvds_mtcnn":
            faceDetectorObject = FaceDetectorFactory.build_movidius_mtcnn()
        elif face_detector_type == "caffe_mtcnn":
            faceDetectorObject = FaceDetectorFactory.build_caffe_mtcnn()
        else:
            print("ERROR: Invalid face detector type")

        faceDetectorThread = FaceDetectorThread(faceDetectorObject)
        faceDetectorThread.start()

        # Start webcam
        camera = cv2.VideoCapture(0)
        ret, image = camera.read()
        cv2.imshow('img', image)

        # init FPS calc
        start_time = time.time()
        processed_frames = 0

        while True:

            # Read frame from Webcam
            ret, image = camera.read()

            # Detect faces
            faceDetectorThread.set_image(image)

            if faceDetectorThread.rects_ready():

                # Get bounding boxes
                rects = faceDetectorThread.get_rects()

                # Draw bounding boxes
                drawBoxes(image, rects, (0, 0, 255))

                # FPS calc
                processed_frames += 1

            # Show image on screen
            cv2.imshow('img', image)

            # Check for exit button 'q'
            ch = cv2.waitKey(1) & 0xFF
            if ch == ord("q"):
                break

        faceDetectorThread.stop()
        faceDetectorThread.join()

        # FPS calc
        total_time = time.time() - start_time
        print("FPS: " + str(processed_frames / total_time))
