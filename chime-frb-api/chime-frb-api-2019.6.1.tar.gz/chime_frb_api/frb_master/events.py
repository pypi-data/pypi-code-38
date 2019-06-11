#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API
import datetime
import logging

log = logging.getLogger(__name__)


class Events(API):
    """
    CHIME/FRB Events API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_event(self, event_number: int = None, full_header: bool = False):
        """
        Get CHIME/FRB Event Information

        Parameters
        ----------
        event_number : int
            CHIME/FRB Event Number

        full_header : bool
            Get the full event from L4, default is False

        Returns
        -------
        dict
        """
        if event_number is None:
            return "event_number is required."
        if full_header:
            return self._get("/v1/events/full-header/{}".format(event_number))
        else:
            return self._get("/v1/events/{}".format(event_number))

    def add_measured_parameters(
        self,
        event_number: int = None,
        pipeline_name: str = None,
        pipeline_status: str = None,
        pipeline_log: str = "",
        **kwargs,
    ):
        """
        Append a new set of measured parameters to CHIME/FRB Event

        Parameters
        ----------
        pipeline_name : str
            Name of the pipeline used to generate measured parameters

        pipeline_status: str
            Status of the pipeline, sample values are 
            
            SCHEDULED
            IN PROGRESS
            COMPLETE
            ERROR
            UNKNOWN
        
        pipeline_log: str
            Small message describing the pipeline run.

        **kwargs : dict
            dictionary of measured parameters to update, valid values are
            
            dm : float
            dm_error : float
            width : float
            snr : float
            dm_index : float
            dm_index_error : float
            flux : float
            flux_error : float
            fluence : float
            fluence_error : float
            scattering_index : float
            scattering_index_error : float
            scattering_timescale : float
            scattering_timescale_error : float
            linear_polarization_fraction : float
            linear_polarization_fraction_error : float
            circular_polarization_fraction : float
            circular_polarization_fraction_error : float
            spectral_index : float
            spectral_index_error : float
            rotation_measure : float
            rotation_measure_error : float
            redshift_host : float
            redshift_host_error : float
            dispersion_smearing : float
            dispersion_smearing_error : float
            spin_period : float
            spin_period_error : float
            ra : float
            ra_error : float
            dec : float
            dec_error : float
            gl : float
            gb : float
            system_temperature : float
            beam_number : int
            galactic_dm : dict
            gain : list
            expected_spectrum: list

        Returns
        -------
            db_response : dict
        """
        valid_int_args = ["beam_number"]
        valid_float_args = [
            "dm",
            "dm_error",
            "width",
            "snr",
            "dm_index",
            "dm_index_error",
            "flux",
            "flux_error",
            "fluence",
            "fluence_error",
            "scattering_index",
            "scattering_index_error",
            "scattering_timescale",
            "scattering_timescale_error",
            "linear_polarization_fraction",
            "linear_polarization_fraction_error",
            "circular_polarization_fraction",
            "circular_polarization_fraction_error",
            "spectral_index",
            "spectral_index_error",
            "rotation_measure",
            "rotation_measure_error",
            "redshift_host",
            "redshift_host_error",
            "dispersion_smearing",
            "dispersion_smearing_error",
            "spin_period",
            "spin_period_error",
            "ra",
            "ra_error",
            "dec",
            "dec_error",
            "gl",
            "gb",
            "system_temperature",
        ]
        valid_dict_args = ["galactic_dm"]
        valid_list_args = ["gain", "expected_spectrum"]

        assert pipeline_name is not None, "parameter: pipeline_name is required"
        assert pipeline_status is not None, "parameter: pipeline_status is required"
        assert event_number is not None, "parameter: event_number is required"
        assert len(kwargs.keys()) > 0, "no parameters updated"

        payload = {
            "datetime": datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M:%S.%f %Z%z"
            ),
            "pipeline": {
                "name": pipeline_name,
                "status": pipeline_status,
                "logs": pipeline_log,
            },
        }

        # Check if the args are valid
        for arg in kwargs.keys():
            assert (
                arg in valid_int_args
                or valid_float_args
                or valid_dict_args
                or valid_list_args
            ), "parameter: {} is not valid".format(arg)

        for arg in kwargs.keys():
            try:
                if arg in valid_int_args:
                    assert (
                        type(kwargs[arg]) is int
                    ), "parameter: {} has to be int".format(arg)
                elif arg in valid_float_args:
                    assert (
                        type(kwargs[arg]) is float
                    ), "parameter: {} has to be float".format(arg)
                elif arg in valid_dict_args:
                    assert (
                        type(kwargs[arg]) is dict
                    ), "parameter: {} has to be dict".format(arg)
                elif arg in valid_list_args:
                    assert (
                        type(kwargs[arg]) is list
                    ), "parameter: {} has to be list".format(arg)
                else:
                    raise NameError("unrecogonized arg: {}".format(arg))
            except AssertionError as e:
                if arg in valid_int_args:
                    kwargs[arg] = int(kwargs[arg])
                    assert (
                        type(kwargs[arg]) is int
                    ), "parameter: {} has to be int".format(arg)
                elif arg in valid_float_args:
                    kwargs[arg] = float(kwargs[arg])
                    assert (
                        type(kwargs[arg]) is float
                    ), "parameter: {} has to be float".format(arg)
            payload[arg] = kwargs[arg]
        url = "/v1/events/measured-parameters/{}".format(event_number)
        response = self._put(url=url, payload=payload)
        return response
