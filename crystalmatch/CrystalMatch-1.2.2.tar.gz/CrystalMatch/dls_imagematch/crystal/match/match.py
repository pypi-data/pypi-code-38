import logging

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.util.status import StatusFlag


class CrystalMatchStatus(StatusFlag):
    pass

# Status values
CRYSTAL_MATCH_STATUS_STATUS_NOT_SET = CrystalMatchStatus(-1, "NOT SET")
CRYSTAL_MATCH_STATUS_OK = CrystalMatchStatus(1, "OK")
CRYSTAL_MATCH_STATUS_FAIL = CrystalMatchStatus(0, "FAIL")
CRYSTAL_MATCH_STATUS_DISABLED = CrystalMatchStatus(2, "DISABLED")


class CrystalMatch:
    """  Represents a match between the position of a crystal in two separate images. """
    def __init__(self, start_point, aligned_images, perform_poi=True):
        """
        Initialize a new CrystalMatch object. Note that You must call the set_feature_match_result
        method to set the transformation (and therefore calculate the matching position in Image 2).
        :param start_point: The user selected location of the crystal in image 1 (in pixels)
        :param aligned_images: AlignedImages object from ImageAligner
        """
        self._aligned_images = aligned_images
        self._poi_image_1 = start_point
        self._poi_image_2_pre_match = start_point + self._aligned_images.pixel_offset()
        self._poi_image_2_matched = None
        self._feature_match_result = None
        self._status = CRYSTAL_MATCH_STATUS_STATUS_NOT_SET if perform_poi else CRYSTAL_MATCH_STATUS_DISABLED
        self._poi_z_level = None

    def is_success(self):
        return self._status == CRYSTAL_MATCH_STATUS_OK

    def has_matched(self):
        """ Returns true if the feature match has been set, regardless of success. """
        return self._status != CRYSTAL_MATCH_STATUS_STATUS_NOT_SET

    def feature_match_result(self):
        return self._feature_match_result

    def get_poi_image_1(self):
        """ The user-specified location of the crystal in Image 1 (in pixels). """
        return self._poi_image_1

    def get_poi_image_1_real(self):
        """ The user-specified location of the crystal in Image 1 (in um). """
        return self._poi_image_1 * self._aligned_images.get_working_resolution()

    def get_poi_image_2_pre_match(self):
        """
        The location of the POI on image 2 before matching (ie: the POI on image 1 with the alignment transform applied.
        """
        return self._poi_image_2_pre_match

    def get_poi_image_2_matched(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        pixels). Note that the set_feature_match_result method must be called to set this to a valid
        value. """
        return self._poi_image_2_matched

    def get_poi_image_2_matched_real(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        um). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._poi_image_2_matched * self._aligned_images.get_working_resolution()

    def get_delta(self):
        """
        Returns the offset which maps the pre-match POI in image 2 to the final point in image 2.
        """
        return self.get_transformed_poi() - self._poi_image_2_pre_match

    def get_delta_real(self):
        return self.get_delta() * self._aligned_images.get_working_resolution()

    def get_transformed_poi(self):
        """
        If the match is a success this returns the final point in image B, if not then it should return the
        offset POI from Image a (ie: the original POI with the Alignment transform applied to map it to image 2).
        """
        if self.is_success():
            return self._poi_image_2_matched
        else:
            return self._poi_image_2_pre_match

    def get_status(self):
        return self._status

    def set_poi_z_level(self, level):
        self._poi_z_level = level

    def get_poi_z_level(self):
        return self._poi_z_level

    def set_feature_match_result(self, feature_result):
        """ Set the transformation which maps the crystal location from Image 1 onto the
        same crystal location on Image 2. """
        self._feature_match_result = feature_result
        trans = feature_result.transform()
        if trans is not None:
            self._status = CRYSTAL_MATCH_STATUS_OK
            # The transform is calculated from image 1 to image 2 - Apply the transform to original POI in image 1
            self._poi_image_2_matched = trans.transform_points([self._poi_image_1])[0]
        else:
            self._status = CRYSTAL_MATCH_STATUS_FAIL

    def print_to_log(self, crystal_id=None):
        """
        Print the current configuration of the CrystalMatch object to the log information. Base information given by
        INFO with detailed info using DEBUG flag.
        :param crystal_id: Optionally print the id for the crystal - can be string or number
        """
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        extra = self._status.to_json_array_with_names('match_stat_num', 'match_stat')

        user_pos_x_px = "{:.2f}".format(self.get_poi_image_1().x)
        user_pos_y_px = "{:.2f}".format(self.get_poi_image_1().y)
        user_pos_x_um = "{:.6f}".format(self.get_poi_image_1_real().x)
        user_pos_y_um = "{:.6f}".format(self.get_poi_image_1_real().y)

        extra.update({'user_pos_x_px': user_pos_x_px,
                     'user_pos_y_px': user_pos_y_px,
                     'user_pos_x_um': user_pos_x_um,
                     'user_pos_y_um': user_pos_y_um})

        if self.is_success():
            match_mean_error = "{:.4f}".format(self._feature_match_result.mean_transform_error())
            match_time = "{:.4f}".format(self._feature_match_result.time_match())
            match_transform = "{:.4f}".format(self._feature_match_result.time_transform())

            beam_pos_x_px = "{:.2f}".format(self.get_poi_image_2_matched().x)
            beam_pos_y_px = "{:.2f}".format(self.get_poi_image_2_matched().y)
            beam_pos_x_um = "{:.6f}".format(self.get_poi_image_2_matched_real().x)
            beam_pos_y_um = "{:.6f}".format(self.get_poi_image_2_matched_real().y)

            beam_pos_z = str(self.get_poi_z_level())

            crystal_movement_x_px = "{:.2f}".format(self.get_delta().x)
            crystal_movement_y_px = "{:.2f}".format(self.get_delta().y)
            crystal_movement_x_um = "{:.6f}".format(self.get_delta_real().x)
            crystal_movement_y_um = "{:.6f}".format(self.get_delta_real().y)

            extra.update({'match_mean_error' : match_mean_error,
                          'match_time': match_time,
                          'match_transform': match_transform,
                          'beam_pos_x_px': beam_pos_x_px,
                          'beam_pos_y_px': beam_pos_y_px,
                          'beam_pos_x_um': beam_pos_x_um,
                          'beam_pos_y_um': beam_pos_y_um,
                          'beam_pos_z': beam_pos_z,
                          'crystal_movement_x_px': crystal_movement_x_px,
                          'crystal_movement_y_px': crystal_movement_y_px,
                          'crystal_movement_x_um': crystal_movement_x_um,
                          'crystal_movement_y_um': crystal_movement_y_um})
        log = logging.LoggerAdapter(log, extra)

        if crystal_id is not None:
            log.info("*** Crystal Match " + str(crystal_id) + " ***")
            log.debug(extra)
        else:
            log.info("*** Crystal Match ***")
            log.debug(extra)

