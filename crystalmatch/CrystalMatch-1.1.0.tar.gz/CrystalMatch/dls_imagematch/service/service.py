import logging
import time

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.crystal.align import AlignConfig
from CrystalMatch.dls_imagematch.crystal.align import ImageAligner
from CrystalMatch.dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_OK
from CrystalMatch.dls_imagematch.crystal.match import CrystalMatchConfig
from CrystalMatch.dls_imagematch.crystal.match import CrystalMatcher
from CrystalMatch.dls_imagematch.crystal.match.match import CrystalMatchStatus
from CrystalMatch.dls_imagematch.feature.detector import DetectorConfig
from CrystalMatch.dls_imagematch.service.service_result import ServiceResult
from CrystalMatch.dls_util.imaging import Image


class CrystalMatch:
    def __init__(self, config_directory, scale_override=None):
        """
        Create a Crystal Matching Service object using the configuration parameters provided.
        :param log_dir: Path override for the log directory.
        :param verbose: Activates verbose logging to std_out.
        :param debug: Activates debugging logging to std_out - overrides verbose mode.
        :param scale_override: Optional override for the pixel sizes of both images - can be None or a
        tuple of the form: ([formulatrix image pixel size], [beam line image pixel size])
        :param job_id: Optional parameter for command line - returned in results to identify the run.
        """
        self._config_directory = config_directory

        self._config_detector = DetectorConfig(config_directory)
        self._config_align = AlignConfig(config_directory, scale_override=scale_override)
        self._config_crystal = CrystalMatchConfig(config_directory)

    def perform_match(self, parser_manager):
        """
        Perform image alignment and crystal matching returning a results object.
        :param .
        :return: ServiceResult object.
        """
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        extra = self._config_align.all_to_json()
        extra.update(self._config_crystal.all_to_json())
        log = logging.LoggerAdapter(log, extra)
        log.info("Matching Started")
        log.debug(extra)

        input_poi = parser_manager.parse_selected_points_from_args()
        beamline_image = parser_manager.get_focused_image()
        parser_manager.save_focused_image(beamline_image)
        focused_image_path = parser_manager.get_focused_image_path()
        formulatrix_image_path = parser_manager.get_formulatrix_image_path()
        job_id = parser_manager.get_job_id()

        # Create the images
        image1 = Image.from_file(formulatrix_image_path)
        image2 = beamline_image

        # Create results object
        service_result = ServiceResult(job_id, formulatrix_image_path, focused_image_path)

        # Perform alignment
        try:

            aligned_images, scaled_poi = self._perform_alignment(image1, image2, input_poi)
            service_result.set_image_alignment_results(aligned_images)

            # Perform Crystal Matching - only proceed if we have a valid alignment
            if aligned_images.alignment_status_code() == ALIGNED_IMAGE_STATUS_OK:
                match_results = self._perform_matching(aligned_images, scaled_poi, parser_manager)

                service_result.append_crystal_matching_results(match_results)

        except Exception as e:
            log.error("ERROR: " + e.message)
            service_result.set_err_state(e)

        return service_result

    def _perform_alignment(self, formulatrix_image, beamline_image, formulatrix_points):
        """
        Perform alignment on the two images, returning an AlignedImages object. As the formulatrix image will be
        scaled the formulatrix_points will alos be scaled to map to the new resolution.
        :param formulatrix_image: image on which points are selected (this will be resized)
        :param beamline_image: image onto which points are projected
        :param formulatrix_points: points on the formulatrix image - these will be rescaled along
        with the formulatrix_image
        :return: An AlignedImages object and a scaled array of formulatrix points.
        """
        aligner = ImageAligner(formulatrix_image, beamline_image, self._config_align, self._config_detector)
        aligned_images = aligner.align()
        scaled_formulatrix_points = aligner.scale_points(formulatrix_points)
        self._log_alignment_status(aligned_images)

        return aligned_images, scaled_formulatrix_points

    def _perform_matching(self, aligned_images, selected_points, parser_manager):

        time_start = time.time()
        matcher = CrystalMatcher(aligned_images, self._config_detector)
        matcher.set_fft_images_to_stack(parser_manager.get_fft_images_to_stack())
        matcher.set_from_crystal_config(self._config_crystal)

        crystal_match_results = matcher.match(selected_points)
        self._log_matching_time(time.time() - time_start)

        return crystal_match_results

    @staticmethod
    def _log_matching_time(time):
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        extra = {'matching_time': time}
        log = logging.LoggerAdapter(log, extra)
        log.info("Matching Complete")
        log.debug(extra)

    @staticmethod
    def _log_alignment_status(aligned):
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        status = "Unknown"

        if aligned.is_alignment_good():
            status = CrystalMatchStatus(2, "Good Alignment")
        elif aligned.is_alignment_poor():
            status = CrystalMatchStatus(1, "Poor Alignment")
        elif aligned.is_alignment_bad():
            status = CrystalMatchStatus(0, "Alignment failed!")

        json_array = status.to_json_array_with_names('align_stat_num', 'align_stat')
        json_array.update({'align_score': aligned.overlap_metric()})

        alignment_transform_scale, alignment_transform_offset = aligned.get_alignment_transform()

        match_result = aligned.feature_match_result
        if match_result is not None:
            match_time = '{:.4f}'.format(match_result.time_match())
            transform_time = '{:.4f}'.format(match_result.time_transform())
            scale = '{:.4f}'.format(alignment_transform_scale)
            transform_x = '{:.4f}'.format(alignment_transform_offset.x)
            transform_y = '{:.4f}'.format(alignment_transform_offset.y)
            json_array.update({'align_time': match_time,
                               'align_trnsf_time:': transform_time,
                               'align_scale': scale,
                               'align_trnsf_x': transform_x,
                               'align_trnsf_y': transform_y
                               })# updates if exists, else adds
        log = logging.LoggerAdapter(log, json_array)
        log.info("Alignment Complete, status: " + status.__str__())
        log.debug(json_array)
