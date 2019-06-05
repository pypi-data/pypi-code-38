#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API


class Distributor(API):
    """
    CHIME/FRB Backend Distributor API

    Attributes
    ----------
    base_url : str
        Base URL at which the distributor is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8002"):
        API.__init__(self, base_url=base_url)

    def create_distributor(self, distributor_name: str, cleanup: bool = False):
        """
        Create a distributor on the CHIME/FRB Backend

        Parameters
        ----------
        distributor_name : str
            Name of the distributor
        cleanup : boolean, optional
            Removes the work from status queue once it is successfully concluded.
            (Default is False)
        """
        payload = {"distributor": distributor_name, "cleanup": cleanup}
        return self._post("/distributor/", payload)

    def stop_distributor(self, distributor_name: str):
        """
        Stops the distributor from accumulating new work,
        whether it is scanning a directory or accpeting work at an endpoint,
        however it continues to distribute work

        Parameters
        ----------
        distributor_name : str
            Name of the distributor
        """
        return self._get("/distributor/stop/{}".format(distributor_name))

    def delete_distributor(self, distributor_name: str):
        """
        Delete a distributor on the CHIME/FRB Backend

        Parameters
        ----------
        distributor_name : str
            Name of the distributor
        """
        return self._delete("/distributor/{}".format(distributor_name))

    def create_directory_scanning_distributor(
        self,
        distributor_name: str,
        directory: str,
        interval: int = 1,
        retries: int = 120,
        cleanup: bool = False,
    ):
        payload = {
            "distributor": distributor_name,
            "directory": directory,
            "interval": interval,
            "retries": retries,
            "cleanup": cleanup,
        }
        """
        Create a Distributor to scan a directory.

        Parameters
        ----------
        distributor : str
            Name of the distributor

        directory : str
            Absolute path to the glob files on, e.g. /frb-archiver/2018/02/01/*.h5

        interval : int, optional
            Scanning interval of the folder in seconds (default is 1)

        retries : int, optional
            Number of retries before the distributor stops (default is 120)

        cleanup : boolean, optional
            Delete work if successfully completed (default is False)
        """
        return self._post("/distributor/directory-scanner", payload)

    def deposit_work(self, distributor_name: str, work):
        """
        Deposit work into a distributor

        Parameters
        ----------
        distributor : str
            Name of the distributor

        work : JSON Encodeable
            List of json encodeable values

        Returns
        -------
            list
        """
        payload = {"work": [work]}
        return self._post("/distributor/work/{}".format(distributor_name), payload)

    def get_work(self, distributor_name: str):
        """
        Get work from a distributor

        Parameters
        ----------
        distributor : str
            Name of the distributor
        """
        return self._get("/distributor/work/{}".format(distributor_name))

    def conclude_work(self, distributor_name, work_name: str, work_status: bool):
        """
        Conclude work managed by a distributor

        Parameters
        ----------
        distributor : str
            Name of the distributor

        work_name
            Work processed

        work_status: bool
            bool defining pass/fail status of work
        """
        payload = {"work": work_name, "status": work_status}
        return self._post(
            "/distributor/conclude-work/{}".format(distributor_name), payload
        )

    def get_status(self, distributor_name: str = None):
        """
        Get status of CHIME/FRB Distributor Backend

        Parameters
        ----------
        distributor_name : str, optional
            Name of the distributor

        Returns
        -------
        json
        """
        if distributor_name is None:
            response = self._get("/distributor/status")
        else:
            response = self._get("/distributor/status/{}".format(distributor_name))
        return response
