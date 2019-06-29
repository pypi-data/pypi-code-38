import cv2
from difflib import SequenceMatcher
from urltools import compare as url_compare
from traceback import format_exc
import validators as url_validator
import numpy as np
import imageio
from scipy.linalg import norm
from scipy import sum, average


class PaginationpageChangeDetection:
    """
    detection algorithm for multiple use cases and return probabilistic view of page changes
    """

    def __init__(self):
        self.prev_url = None
        self.curr_url = None
        self.prev_screen_shot_uri = None
        self.curr_screen_shot_uri = None
        self.prev_content = None
        self.curr_content = None
        self.threshold_content = 0.9
        self.threshold_for_contour_change_ratio = 0.01
        self.invalid_para_list = []

    def set_threshold_content(self, new_threshold_value):
        self.threshold_content = new_threshold_value

    def set_threshold_for_contour_change_ratio(self, new_threshold_value):
        self.threshold_for_contour_change_ratio = new_threshold_value

    def set_prev_url(self, prev_url):
        """
        setter with validation
        :param prev_url: previous url
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if type(prev_url) is str:
                if url_validator.url(prev_url):
                    self.prev_url = prev_url
                    return True
            self.invalid_para_list.append("prev_url")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("prev_url")
            return False

    def set_curr_url(self, curr_url):
        """
        setter with validation
        :param curr_url: current URL
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if type(curr_url) is str:
                if url_validator.url(curr_url):
                    self.curr_url = curr_url
                    return True
            self.invalid_para_list.append("curr_url")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("curr_url")
            return False

    def set_prev_screen_shot(self, prev_screen_shot):
        """
        setter with validation
        :param prev_screen_shot: previous screenshot
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            print(type(prev_screen_shot))
            if type(prev_screen_shot) is str:
                self.prev_screen_shot_uri = prev_screen_shot
                return True
            self.invalid_para_list.append("prev_screen_shot")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("prev_screen_shot")
            return False

    def set_curr_screen_shot(self, curr_screen_shot):
        """
        setter with validation
        :param curr_screen_shot: current screen shot
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if type(curr_screen_shot) is str:
                self.curr_screen_shot_uri = curr_screen_shot
                # print("set screenshot1" + self.curr_screen_shot_uri)
                return True
            self.invalid_para_list.append("curr_screen_shot")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("curr_screen_shot")
            return False

    def set_prev_content(self, prev_content):
        """
        setter with validation
        :param prev_content: previous content.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if type(prev_content) is str:
                self.prev_content = prev_content
                return True
            self.invalid_para_list.append("prev_content")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("prev_content")
            return False

    # noinspection PyBroadException
    def set_curr_content(self, curr_content):
        """
        setter with validation
        :param curr_content: current content
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if type(curr_content) is str:
                self.curr_content = curr_content
                return True
            self.invalid_para_list.append("curr_content")
            return False
        except Exception as e:
            print(format_exc())
            self.invalid_para_list.append("curr_content")
            return False

    @staticmethod
    def get_screen_shot_image(screen_shot_path):
        """
        load image
        :param screen_shot_path: **Full path of screenshot.
        :return:
            np.ndarray -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            return cv2.imread(screen_shot_path)
        except Exception as e:
            print(format_exc())
            return False

    def get_report(self, prev_url, curr_url, prev_screen_shot, curr_screen_shot, prev_content, curr_content):
        """
        returns report about whether change is detected or not.
        :param prev_url: previous URL
        :param curr_url: current URL
        :param prev_screen_shot: previous screen_shot
        :param curr_screen_shot: current screen_shot
        :param prev_content: previous content
        :param curr_content: current content
        :return:
            [True, None] -> if change is detected
            OR
            [False, self.invalid_para_list] -> if change not detected or exception occurred
        """
        self.set_prev_url(prev_url)
        self.set_curr_url(curr_url)
        self.set_prev_screen_shot(prev_screen_shot)
        self.set_curr_screen_shot(curr_screen_shot)
        self.set_prev_content(prev_content)
        self.set_curr_content(curr_content)
        if len(self.invalid_para_list) != 0:
            return False, self.invalid_para_list
        url_result = self.get_percentage_change_in_url()
        content_result = self.get_percentage_change_in_page_content()
        screen_shot_result = self.get_percentage_change_in_screen_shot()
        print("#Url result :", url_result)
        print("#Content result :", content_result)
        print("#Screen shot result :", screen_shot_result)
        if sum([url_result, screen_shot_result, content_result]) >= 2:
            return True, None
        else:
            print("###Returning not matched###")
            return False, self.invalid_para_list

    def get_percentage_change_in_url(self):
        """
        checks whether change in URL.
        :return:
            True -> Change detected in URL.
            OR
            False -> Change NOT detected in URL.
        """
        try:
            method_url_tools = self.change_in_url_by_url_tools()
            method_url_difference = self.change_in_url_by_difference()
            if sum([method_url_tools, method_url_difference]) > 1:
                return True
            else:
                return False
        except Exception as e:
            print(format_exc())
            return False

    def get_percentage_change_in_page_content(self):
        """
        This function compares page content and returns wheither change in page content or not.
        :return:
            True -> if change detected in page content
            OR
            False-> if NO change detected in page content
        """
        try:
            percentage_change_in_content = self.compare_text()

            if percentage_change_in_content is not False:
                # if percentage_change_in_content > 0.1 (1.0 - 0.9(for now) )
                if percentage_change_in_content > (1.0 - self.threshold_content):
                    print("text is not matched, threshold is : " + str(self.threshold_content))
                    return True
                print("text is matched, threshold" + str(self.threshold_content))
            return False
        except Exception as e:
            print(format_exc())
            return False

    def get_percentage_change_in_screen_shot(self):
        """
        This function detects change in screenshots.
        :return:
            True -> if change detected
            OR
            False-> if No change detected
        """
        try:
            prev_data = self.prev_screen_shot_uri
            if prev_data is False:
                return False
            curr_data = self.curr_screen_shot_uri
            if curr_data is False:
                return False
            cv2_result = self.compare_image_by_cv2(prev_data, curr_data)
            m_norm_result, z_norm_result = self.compare_image_by_manhattan_and_zero_norm(prev_data, curr_data)
            print("cv2 and norm result :" + str(cv2_result) + str(m_norm_result) + str(z_norm_result))
            if sum([cv2_result, m_norm_result, z_norm_result]) > 1:
                return True
            else:
                return False
        except Exception as e:
            print(format_exc())
            return False

    def change_in_url_by_url_tools(self):
        """
        This function returns whether there is change in URL by comparing URL using urltool.

        :return:
            True -> If change detected
            OR
            False-> If No change detected.
        """
        try:
            # url_compare returns True if both urls are same.
            # But we have to return True if urls are change (So not is used)
            return not url_compare(self.prev_url, self.curr_url)
        except Exception as e:
            print(format_exc())
            return False

    def change_in_url_by_difference(self):
        """
        This function returns whether there is change in URL by string comparision.
        :return:
            True -> If change detected OR
            False-> If No change detected.
        """
        try:
            sequence_match = SequenceMatcher(None, self.prev_url, self.curr_url)
            ratio_url_match = sequence_match.ratio()

            if ratio_url_match < 1.0:
                print("Ratio of similarity in URL : " + str(ratio_url_match))
                return True
            else:
                return False

        except Exception as e:
            print(format_exc())
            return False

    def compare_text(self):
        """
        This function uses "gestalt pattern matching" algorithm published by Ratcliff and Obershelp in 1980's
        :return:
            ration_of_change :- float value represents ratio of change between text_A and text_B
                                    ** Value is between 0 and 1
            OR
            False -> if execution failed
        """
        try:
            seq_match = SequenceMatcher(None, self.prev_content, self.curr_content)
            ratio_of_similarity = seq_match.ratio()
            ration_of_change = 1.0 - ratio_of_similarity
            print("ratio os change is :" + str(ration_of_change))
            return ration_of_change
        except Exception as e:
            print(format_exc())
            return False

    def compare_image_by_cv2(self, image_one, image_two):
        """
        This function compares 2 images, and find ratio of change.
        Based on ratio returns boolean value.
        :param image_one: (np.ndarray or image full path) image
        :param image_two: (np.ndarray or image full path) image
        :return:
            True -> If change detected in images
            OR
            False -> No change detected in images
        """
        try:
            try:
                # print(type(image_one))
                if type(image_one) == str:
                    image_one = cv2.imread(image_one, 0)
                    print("read image 1")
                if type(image_two) == str:
                    image_two = cv2.imread(image_two, 0)
                    print("read image 2")
            except Exception:
                raise Exception("Error in load image")
            try:
                # print("set screenshot2" + self.prev_screen_shot_uri)
                image_one_h, image_one_w = image_one.shape[:2]
                image_two_h, image_two_w = image_two.shape[:2]
                # print("height and width : image1 : " + str(image_one_h) + str(image_one_w))
                # print("height and width : image2 : " + str(image_two_h) + str(image_two_w))
            except Exception as e:
                raise Exception("Error in load height and width")
            bottom_padding_value = (max(image_one_h, image_two_h) - min(image_one_h, image_two_h))
            if min(image_one_h, image_two_h) == image_one_h:
                image_one = cv2.copyMakeBorder(image_one, 0, bottom_padding_value, 0, 0, cv2.BORDER_CONSTANT, value=0)
            if min(image_one_h, image_two_h) == image_two_h:
                image_two = cv2.copyMakeBorder(image_two, 0, bottom_padding_value, 0, 0, cv2.BORDER_CONSTANT, value=0)
            difference_in_image = cv2.subtract(image_one, image_two)
            # convert color image to gray scale
            # difference_in_gray_scale = cv2.cvtColor(difference_in_image, cv2.COLOR_BGR2GRAY)
            # apply threshold to image
            thresh = cv2.threshold(difference_in_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            # find contours
            # Refer : https://docs.opencv.org/3.1.0/d4/d73/tutorial_py_contours_begin.html
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # Refer for hierarchy : https://docs.opencv.org/trunk/d9/d8b/tutorial_py_contours_hierarchy.html
            # [Next, Previous, First_Child, Parent]
            print("len(contours) :", len(contours))
            print('first contour : ', contours[0])
            print("hierarchy of contour : ", hierarchy)
            hierarchy = hierarchy[0]
            # Refer for hierarchy : https://docs.opencv.org/trunk/d9/d8b/tutorial_py_contours_hierarchy.html
            # [Next, Previous, First_Child, Parent]
            #  0       1       2            3
            filtered_contours = []
            for component in zip(contours, hierarchy):
                current_contour = component[0]
                current_hierarchy = component[1]
                # filter contours where parent == 0
                if current_hierarchy[3] == 0:
                    filtered_contours.append(current_contour)

            total_contours_area = 0.0
            print("len(contours) :", len(filtered_contours))
            # add detected contours area into total_contours_area
            for cnt in filtered_contours:
                area = cv2.contourArea(cnt)
                # print("con :", cnt, " area :", area)
                total_contours_area += area
            # cv2.imwrite("diff_image.png", difference_in_image)
            # cv2.imwrite("diff_image_thresholded.png", thresh)
            cv2.drawContours(image_one, contours, -1, (0, 255, 0), 3)
            cv2.imwrite('test_images\\draw_contours.png', image_one)
            diff_img_height, diff_img_width = difference_in_image.shape[:2]
            print("Diff image (h,w):", (diff_img_height, diff_img_width))
            # change_ratio = contours_area / diff_img_area
            print("Total top level contour area :", str(total_contours_area))
            print("Total image are : ", (diff_img_height * diff_img_width))
            # calculate change ratio
            change_ratio = total_contours_area / (diff_img_height * diff_img_width)
            print("screenshot Change ratio : ", change_ratio)
            # if change_ratio > 0.1 (1.0 - 0.9 for now) , Then there is change in screenshots
            # So return True
            print(self.threshold_for_contour_change_ratio)
            if change_ratio > self.threshold_for_contour_change_ratio:
                return True
            else:
                return False
        except Exception as e:
            print(format_exc())
            return False

    def to_grayscale(self, arr):
        """
        If arr is a color image (3D array), convert it to gray scale (2D array).
        :param arr: image object array.
        :return:
            arr : image array converted in gray scale.
        """
        try:
            if len(arr.shape) == 3:
                return average(arr, -1)  # average over the last axis (color channels)
            else:
                return arr
        except Exception as e:
            print(format_exc())
            return arr

    def normalize(self, arr):
        """
        this function will normalize the given array
        :param arr: image object
        :return:
            normalised array
        """
        try:
            rng = arr.max() - arr.min()
            amin = arr.min()
            return (arr - amin) * 255 / rng
        except Exception as e:
            print(format_exc())
            return arr

    def compare_image_by_manhattan_and_zero_norm(self, img1, img2):
        """
        this method will return comparison result of two images with same or different size by mahattan and zero norm method.
        (refer : https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images)
        :param img1: (str) image one full path.
        :param img2: (str) image two full path.
        :return:
            m_norm_decision, z_norm_decision -> true or false on the basis of result of manhatttan and zero norm.
            OR
            False, False -> if any exception occurred.
        """
        try:
            img1 = self.to_grayscale(imageio.imread(img1).astype(float))
            img2 = self.to_grayscale(imageio.imread(img2).astype(float))
            img1_height, img1_width = img1.shape[:2]
            img2_height, img2_width = img2.shape[:2]
            if min(img1_height, img2_height) == img1_height:
                # make plane canvas of size of image 1
                im_bg = np.zeros((img2_height, img2_width))
                # paint canvas black
                im_bg = (im_bg + 1) * 0  # make black
                # if pad_top =0 : padding is done at bottom
                pad_top = 0
                # print image 1 on canvas from stating pixel pad_top
                im_bg[pad_top:pad_top + img1_height, :] = img1
                img1 = im_bg
            elif min(img1_height, img2_height) == img2_height:
                # make plane canvas of size of image 2
                im_bg = np.zeros((img1_height, img1_width))
                # paint canvas black
                im_bg = (im_bg + 1) * 0  # make black
                # if pad_top =0 : padding is done at bottom
                pad_top = 0
                # print image 2 on canvas from stating pixel pad_top
                im_bg[pad_top:pad_top + img2_height, :] = img2
                img2 = im_bg
            # imageio.imwrite('first.png', img1)
            # imageio.imwrite('second.png', img2)
            # normalize to compensate for exposure difference
            img1 = self.normalize(img1)
            img2 = self.normalize(img2)
            # imageio.imwrite('name.png', img1)
            # imageio.imwrite('name1.png', img2)
            print("shape 1 : " + str(img1.shape[:2]))
            print("shape 2 : " + str(img2.shape[:2]))
            # calculate the difference and its norms
            diff = img1 - img2  # element wise for scipy arrays
            m_norm = sum(abs(diff))  # Manhattan norm
            z_norm = norm(diff.ravel(), 0)  # Zero norm
            m_norm_decision = False
            z_norm_decision = False
            # if result of m_norm(mahattan norm) > 1%
            # image is different return true
            if m_norm > 2.5:
                m_norm_decision = True
            # if result of z_norm(zero norm) > 10%
            # image is different return true
            if z_norm > 0.1:
                z_norm_decision = True
            return m_norm_decision, z_norm_decision
        except Exception as e:
            print(format_exc())
            return False, False
