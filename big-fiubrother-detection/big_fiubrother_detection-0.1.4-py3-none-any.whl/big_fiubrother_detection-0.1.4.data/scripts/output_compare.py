import sys
import cv2
import os

def drawBoxes(im, boxes, color):
    x1 = [i[0] for i in boxes]
    y1 = [i[1] for i in boxes]
    x2 = [i[2] for i in boxes]
    y2 = [i[3] for i in boxes]
    for i in range(len(boxes)):
        cv2.rectangle(im, (int(x1[i]), int(y1[i])), (int(x2[i]), int(y2[i])), color, 1)
    return im

if __name__ == "__main__":

    if len(sys.argv) < 4:

        print("--------------------------------")
        print("This script receives files with validation bboxes and test bboxes and shows them in green and red respectively")
        print("")
        print("Usage: ")
        print("python compare_outputs.py 'bb_file_val' 'bb_file_test' 'image_path1' 'image_path2' ... ")
        print("--------------------------------")

    else:

        image_paths = sys.argv[3:]


        # Read bounding boxes from val file
        bb_filename_val = sys.argv[1]
        bb_file_val = open(bb_filename_val, "r")
        bboxes_val = {}

        while (True):
            image_name = bb_file_val.readline().strip()
            if not image_name:
                break
            bboxes_val[image_name] = []

            num_bboxes = int(bb_file_val.readline().strip())
            for j in range(num_bboxes):
                bbox = bb_file_val.readline().strip().split(",")
                bbox[2] = int(bbox[0]) + int(bbox[2])
                bbox[3] = int(bbox[1]) + int(bbox[3])
                bboxes_val[image_name].append(bbox)

        # Read bounding boxes from test file
        bb_filename_test = sys.argv[2]
        bb_file_test = open(bb_filename_test, "r")
        bboxes_test = {}

        while (True):
            image_name = bb_file_test.readline().strip()
            if not image_name:
                break
            bboxes_test[image_name] = []

            num_bboxes = int(bb_file_test.readline().strip())
            for j in range(num_bboxes):
                bbox = bb_file_test.readline().strip().split(",")
                bbox[2] = int(bbox[0]) + int(bbox[2])
                bbox[3] = int(bbox[1]) + int(bbox[3])
                bboxes_test[image_name].append(bbox)

        # Read and display images
        for i in range(len(image_paths)):

            # Read image
            image_path = image_paths[i]
            img = cv2.imread(image_path)

            # Draw bounding boxes
            image_name = os.path.basename(image_path)
            if image_name in bboxes_val:
                img = drawBoxes(img, bboxes_val[image_name], (0, 255, 0))
                pass
            if image_name in bboxes_test:
                img = drawBoxes(img, bboxes_test[image_name], (0, 0, 255))
                pass

            # Show image on screen
            cv2.imshow('img', img)
            ch = cv2.waitKey(0) & 0xFF
            if ch == ord("q"):
                break