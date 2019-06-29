import traceback
from datetime import datetime
from traceback import format_exc
import cv2
import os
import logging


class TemplateMatching:

    def __init__(self):
        # note:- min increment factor must be 1
        self.increment_factor = 1
        # Confidence of detected image should be 0.9 and above
        self.confidence_threshold = 0.9

        self.logger = logging.getLogger()
        log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        fh = logging.FileHandler(filename=os.path.join('log', log_filename))
        self.logger.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.codetype = "Template Matching"

    def get_search_window_coordinates(self, src_height, src_width, template_height, template_width, ref_x, ref_y):
        """
        This function will calculate the values(search_window(xmin,ymin) & search_window(xmax,ymax)) for creating
        search window for template.
        :param src_height: source image height.
        :param src_width: source image width.
        :param template_height: template image height.
        :param template_width: template image width.
        :param ref_x: reference x-value.
        :param ref_y: reference y-value.
        :return:
            xmin, ymin, xmax, ymax -> search window coordinates top-left and bottom-right corner.
        """
        # print(self.increment_factor)
        self.logger.info("get_search_window_coordinates : increment_factor : " + str(self.increment_factor))
        self.logger.info("get_search_window_coordinates : src_height , src_width: " + str((src_height, src_width)))
        self.logger.info("get_search_window_coordinates : template_height , template_width: " + str((template_height, template_width)))

        # max in below statement ensures min value of search_window_height_margin = 1
        # search_window_height_margin=int((template_height*100)/src_height)*(self.increment_factor*self.increment_factor)
        search_window_height_margin = max(1, int((template_height * 100) / src_height)) * (
                self.increment_factor * self.increment_factor)

        cal_height_offset = int((src_height * search_window_height_margin) / 100)

        self.logger.info("get_search_window_coordinates : search_window_height_margin : " + str(search_window_height_margin))

        # co-ordinates with respect to  given point(ref_x,ref_y)
        xmin = 0
        ymin = int(max(0, ref_y - cal_height_offset))
        xmax = src_width
        ymax = int(min(src_height, ref_y + cal_height_offset))
        return xmin, ymin, xmax, ymax

    def search_for_template(self, source_image, template_image):
        """
        This function will search for given template image in given source image and return top_left, bottom_right co-
        ordinates and confidence.we have used matchtemplate() method from cv2 library.
        :param source_image: given source image.
        :param template_image: given template image.
        :return:
            xmin        -> xmin of the detected image.
            ymin        -> ymin of the detected image.
            xmax        -> xmax of the detected image.
            ymax        -> ymax of the detected image.
            confidence  -> confidence of the detected image is exactly template image.
        """
        try:
            if type(source_image) == str:
                source_image = cv2.imread(source_image, 0)
            if type(template_image) == str:
                template_image = cv2.imread(template_image, 0)

        except Exception:
            self.logger.debug("ERROR IN LOADING IMAGES")
            raise Exception("Error in load image")
        try:
            template_img_h, template_img_w = template_image.shape[:2]
            result_img = cv2.matchTemplate(source_image, template_image, cv2.TM_CCOEFF_NORMED)
            # print(result_img)
            # confidence
            #  use cv2.minMaxLoc() function to find where is the maximum/minimum value from result_img.
            # refer : https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
            _, max_val, _, max_loc = cv2.minMaxLoc(result_img)
            top_left = max_loc
            bottom_right = (top_left[0] + template_img_w, top_left[1] + template_img_h)
            template_confidence = max_val
            xmin = top_left[0]
            ymin = top_left[1]
            xmax = bottom_right[0]
            ymax = bottom_right[1]
            return xmin, ymin, xmax, ymax, template_confidence
        except Exception as e:
            print("Problem in search for template")
            self.logger.debug(format_exc())
            return False,False,False,False,False

    def match_template_by_ref_coordinates(self, src_img_file, template_img_file, ref_x, ref_y):
        """
        This method will return top_left, bottom right co-ordinates of identified part from source image.
        :param src_img_file: source image
        :param template_img_file: template image to be find
        :param ref_x: x co-ordinate
        :param ref_y: y co-ordinate
        :return:
            (xmin,ymin) -> top-left x and y co-ordinate of identified part from source image,
            (xmax,ymax) -> bottom-right x and y co-ordinate of identified part from source image,
            confidence  -> value to which image being matched.
            OR
            None        -> if confidence is low Or invalid input is given.

        """
        try:
            start_time = datetime.now()

            self.logger.info("Source Image : " + str(src_img_file) + " Template Image : " + str(template_img_file) + " ref_x : " + str(ref_x) + " ref_y : " + str(ref_y))

            # load images if file path is passed
            try:
                if type(src_img_file) == str:
                    src_img_file = cv2.imread(src_img_file, 0)
                if type(template_img_file) == str:
                    template_img_file = cv2.imread(template_img_file, 0)

            except Exception:
                self.logger.debug("ERROR IN LOADING IMAGES")
                raise Exception("Error in load image")
            # source image height and width
            src_height, src_width = src_img_file.shape[:2]
            # height and width of template_img_file
            template_height, template_width = template_img_file.shape[:2]
            if ref_y > src_height or ref_x > src_width:
                self.logger.debug("ERROR:  INVALID REFERENCE POINT")
                return False, False, False, False, False, 1
                #raise Exception("ERROR : Invalid input: ref_x and ref_y")

            if template_height > src_height and template_width > src_width:
                self.logger.debug("ERROR: TEMPLATE IMAGE SIZE IS LARGER THAN SOURCE IMAGE")
                return False, False, False, False, False, 2
                #raise Exception("ERROR : template image size is larger than src image.")

            self.increment_factor = 1
            trial_count = 0
            while True:
                trial_count += 1
                # cropping image
                self.logger.info("Template matching trial " + str(trial_count))

                search_window_xmin, search_window_ymin, search_window_xmax, search_window_ymax = self.get_search_window_coordinates(
                    src_height, src_width, template_height, template_width, ref_x, ref_y)

                self.logger.info("Template matching search window cordinates : " + str((search_window_xmin, search_window_ymin, search_window_xmax, search_window_ymax)))

                search_window = src_img_file[search_window_ymin: search_window_ymax,
                                search_window_xmin: search_window_xmax]
                # validation : whether the search window smaller than template image.
                search_window_h, search_window_w = search_window.shape[:2]
                # if search_window is smaller than template image search window should be maximized
                if template_width > search_window_w or template_height > search_window_h:
                    self.increment_factor += 1
                    continue
                detected_xmin, detected_ymin, detected_xmax, detected_ymax, detection_confidence = self.search_for_template(
                    search_window, template_img_file)
                # logging
                self.logger.info("template_detection_confidence : " + str(detection_confidence))
                self.logger.info("template_detection_coordinates : " + str((detected_xmin, detected_ymin, detected_xmax, detected_ymax)))

                # for breaking loop.
                if detection_confidence > self.confidence_threshold:
                    # ("Detected image confidence > ideal threshold")
                    self.logger.info("detection_template_confidence > confidence_threshold i.e. " + str(detection_confidence) + " > " + str(self.confidence_threshold))
                    break
                if search_window_ymin == 0 and search_window_ymax == src_height:
                    self.logger.info("complete image scanned")
                    break
                self.increment_factor += 1

            if detection_confidence <= self.confidence_threshold:
                return False, False, False, False, False

            final_xmin = (search_window_xmin + detected_xmin)
            final_ymin = (search_window_ymin + detected_ymin)
            final_xmax = (search_window_xmin + detected_xmax)
            final_ymax = (search_window_ymin + detected_ymax)
            print("Number of trials : ", trial_count)
            end_time = datetime.now()

            time_required = end_time - start_time
            print("Completed template matching in " + str(time_required.total_seconds()) + " seconds.")
            self.logger.info("Completed template matching in " + str(time_required.total_seconds()) + " seconds with " + str(trial_count) + " trials.")

            return final_xmin, final_ymin, final_xmax, final_ymax, detection_confidence,0
        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(format_exc())
            return False, False, False, False, False,3


if __name__ == '__main__':
    pass
