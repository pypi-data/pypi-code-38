from __future__ import print_function

import numpy as np
import logging
import json
from json.encoder import JSONEncoder

from os.path import abspath, join, exists, isdir, splitext, split

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_NOT_SET
from CrystalMatch.dls_imagematch.crystal.match.match import CRYSTAL_MATCH_STATUS_DISABLED
from CrystalMatch.dls_imagematch.util.status import StatusFlag
from CrystalMatch.dls_util.shape.point import Point


class ServiceResultExitCode(StatusFlag):
    def __init__(self, code, status, err_msg=None):
        StatusFlag.__init__(self, code, status)
        self.err_msg = err_msg

    def __str__(self):
        if self.err_msg is None:
            return str(self.code)
        else:
            return str(self.code) + ", " + self.err_msg

    def set_err_msg(self, err_msg):
        self.err_msg = err_msg

    def to_json_array(self):
        json_array = StatusFlag.to_json_array(self)
        if self.err_msg is not None:
            json_array['err_msg'] = self.err_msg
        return json_array

    def to_json_array_with_names(self, code_num, code):
        json_array = StatusFlag.to_json_array_with_names(self, code_num, code)
        if self.err_msg is not None:
            json_array['err_msg'] = self.err_msg
        return json_array


# Status values
SERVICE_RESULT_STATUS_INCOMPLETE = ServiceResultExitCode(-1, "EXITED EARLY")
SERVICE_RESULT_STATUS_COMPLETE = ServiceResultExitCode(0, "COMPLETE")
SERVICE_RESULT_STATUS_ERROR = ServiceResultExitCode(-1, "ERROR")


class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, np.float32):
            # noinspection PyUnresolvedReferences
            return o.item()
        return super(DecimalEncoder, self).default(o)


class ServiceResult:
    """
    NOTE: This should be the only class allowed to print() to the console - elsewhere use logging.
    GDA relays on this feature - reads the jason console output.
    Results class which determines the format and structure of output reported to the console. This is also intended to
    standardise the handling of errors for the wrapper service.
    """

    POI_RESULTS_HEADER = "\nlocation ; transform ; status ; mean error"

    def __init__(self, job_id, formulatrix_image_path, focused_image_path):
        """
        Create a ServiceResult object used to report CrystalMatch results to the console, log file and (optionally)
        image directory.
        :param formulatrix_image_path: Image path for the input image.
        :param beamline_image_path: Image path for the output image.
        """
        self._job_id = job_id
        self.SEPARATOR = " ; "
        self._image_path_formulatrix = abspath(formulatrix_image_path)
        self._image_path_beamline = abspath(focused_image_path)
        self._alignment_transform_scale = 1.0
        self._alignment_transform_offset = Point(0, 0)
        self._alignment_status_code = ALIGNED_IMAGE_STATUS_NOT_SET
        self._alignment_error = 0.0
        self._match_results = []
        self._exit_code = SERVICE_RESULT_STATUS_INCOMPLETE

    def set_image_alignment_results(self, aligned_images):
        """
        Harvest the output data from an image alignment operation.
        :param aligned_images: An AlignedImages object.
        """
        self._alignment_transform_scale, self._alignment_transform_offset = aligned_images.get_alignment_transform()
        self._alignment_status_code = aligned_images.alignment_status_code()
        self._alignment_error = aligned_images.overlap_metric()
        self._exit_code = SERVICE_RESULT_STATUS_COMPLETE

    def set_err_state(self, e):
        """
        Sets the exit code to an error status and copies the error message from the provided exception into the output.
        :param e: Thrown exception.
        """
        self._exit_code = SERVICE_RESULT_STATUS_ERROR
        self._exit_code.set_err_msg(e.message)

    def set_crystal_matching_results(self, list_of_fft_points):
        self._match_results = list_of_fft_points



    def append_crystal_matching_results(self, crystal_matcher_results):
        """
        Append any CrystalMatch objects from a CrystalMatcherResults object into an internal array - necessary when
        #performing multiple passes of the algorithm or when farming points out to multiple processes.
        :param crystal_matcher_results: CrystalMatcherResults object.
        """
        self._match_results = self._match_results + crystal_matcher_results.get_matches()

    def _get_printable_alignment_transform(self):
        return str(self._alignment_transform_scale) + ", " + str(self._alignment_transform_offset)

    def _append_crystal_match_results(self, output_list):
        if len(self._match_results) > 0:
            output_list.append(self.POI_RESULTS_HEADER)
        for crystal_match in self._match_results:
            line = "poi:"
            line += str(crystal_match.get_transformed_poi()) + " z: " +  str(crystal_match.get_poi_z_level()) + self.SEPARATOR
            line += str(crystal_match.get_delta()) + self.SEPARATOR
            line += str(crystal_match.get_status()) + self.SEPARATOR
            if crystal_match.get_status() == CRYSTAL_MATCH_STATUS_DISABLED:
                line += "0"
            else:
                line += str(crystal_match.feature_match_result().mean_transform_error())
            output_list.append(line)

    def print_results(self, jason_output):
        """
        Print the contents of this results object to the console.  Returns the printed object for testing purposes.
        :return : The printed object - JSON mode will return the full json object.
        """
        if jason_output:
            return self._print_json_object()
        return self._print_human_readable()

    def _print_human_readable(self):

        output = []
        if self._job_id and self._job_id != "":
            output = ['job_id:"' + str(self._job_id) + '"']
        output += ['exit_code:' + str(self._exit_code),
                   'input_image:"' + self._image_path_formulatrix + '"',
                   'output_image:"' + self._image_path_beamline + '"',
                   'align_transform:' + self._get_printable_alignment_transform(),
                   'align_status:' + str(self._alignment_status_code),
                   'align_error:' + str(self._alignment_error)
                   ]

        self._append_crystal_match_results(output)

        # Print human readable
        for line in output:
            print(line)
        return output


    def _print_json_object(self):
        output_obj = {'exit_code': self._exit_code.to_json_array()}

        # Global alignment transform
        if self._job_id and self._job_id != "":
            output_obj['job_id'] = str(self._job_id)
        output_obj['input_image'] = self._image_path_formulatrix
        output_obj['output_image'] = self._image_path_beamline
        output_obj['alignment'] = {
            'status': self._alignment_status_code.to_json_array(),
            'mean_error': self._alignment_error,
            'scale': self._alignment_transform_scale,
            'translation': {
                'x': self._alignment_transform_offset.x,
                'y': self._alignment_transform_offset.y,
            }
        }

        # POI description
        poi_array = []
        for poi in self._match_results:
            mean_error = poi.feature_match_result().mean_transform_error() if poi.is_success() else 0
            poi_array.append({
                'location': {
                    'x': poi.get_transformed_poi().x,
                    'y': poi.get_transformed_poi().y,
                    'z': poi.get_poi_z_level()
                },
                'translation': {
                    'x': poi.get_delta().x,
                    'y': poi.get_delta().y,
                },
                'status': poi.get_status().to_json_array(),
                'mean_error': mean_error
            })
        output_obj['poi'] = poi_array
        print(json.dumps(output_obj, cls=DecimalEncoder))
        return output_obj


    def log_final_result(self, total_time):
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        extra = self._exit_code.to_json_array_with_names('exit_code_num', 'exit_code')
        extra.update({'input_image': self._image_path_formulatrix,
                      'output_image': self._image_path_beamline,
                      'total_time': total_time})
        if self._job_id and self._job_id != "":
            extra.update({'job_id': self._job_id})


        log = logging.LoggerAdapter(log, extra)
        log.info("Crystal Match Complete")
        log.debug(extra)

