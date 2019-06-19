from microlab.vision.cameras import Camera
import time
import os

if __name__ == "__main__":
    print('\n~ TEST CAMERA')

    # Initialize vision object
    cam = Camera(index=0)

    # connect to vision
    cam.connect()

    # start the recording
    cam.start()

    # let the vision stream open for a while
    time.sleep(1)

    # stop the recording
    cam.stop()

    # disconnect from vision
    cam.disconnect()

    # save the images
    cam.export(path='frames', verbose=True)

    # clear the images
    # cam.clear(path='frames', verbose=True)
