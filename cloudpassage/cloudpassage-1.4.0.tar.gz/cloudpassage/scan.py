"""Scan and CveException classes"""

import cloudpassage.sanity as sanity
from .utility import Utility as utility
from .exceptions import CloudPassageValidation
from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class Scan(HaloEndpoint):
    """Initializing the Scan class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    """

    supported_scans = {
        "sca": "sca",
        "csm": "sca",
        "svm": "svm",
        "sva": "svm",
        "sam": "sam",
        "fim": "fim",
        "sv": "sv"
    }
    supported_historical_scans = {
        "sca": "sca",
        "csm": "sca",
        "svm": "svm",
        "sva": "svm",
        "fim": "fim"
    }
    supported_scan_status = [
        "queued",
        "pending",
        "running",
        "completed_clean",
        "completed_with_errors",
        "failed"
    ]
    supported_search_fields = [
        "server_id",
        "module",
        "status",
        "since",
        "until"
    ]

    object_name = "scan"
    objects_name = "scans"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def initiate_scan(self, server_id, scan_type):
        """Initiate a scan on a specific server.

        Args:
            server_id (str): ID of server to be scanned
            scan_type (str): Type of scan to be run.

          Valid scan types:
            sca  - Configuration scan
            csm  - Configuration scan (same as sca)
            svm  - Software vulnerability scan
            sva  - Software vulnerability scan (same as svm)
            sam  - Server access management scan
            fim  - File integrity monitoring scan
            sv   - Agent self-verifiation scan

        Returns:
            dict: Dictionary describing command created as a result of this
                call. As this scan is run asynchronously, this method returns
                information on the server command, not the scan itself. The
                server command will, in turn, cause the scan to be performed on
                the server. The ID that can be retrieved from the return value
                of this method can be used with the
                :py:func:`cloudpassage.Server.command_details` method to
                retrieve the status of the scan.

        Raises:
            CloudPassageValidation: Unsupported value for ``scan_type``.
        """

        sanity.validate_object_id(server_id)
        if self.scan_type_supported(scan_type) is False:
            exception_message = "Unsupported scan type: %s" % scan_type
            raise CloudPassageValidation(exception_message)
        else:
            scan_type_normalized = self.supported_scans[scan_type]
            request_body = {"scan": {"module": scan_type_normalized}}
            endpoint = "/v1/servers/%s/scans" % server_id
            request = HttpHelper(self.session)
            response = request.post(endpoint, request_body)
            command_info = response["command"]
            return command_info

    def last_scan_results(self, server_id, scan_type):
        """Get the results of scan_type performed on server_id.

        Args:
            server_id (str): ID of server
            scan_type (str): Type of scan to filter results for

        Valid scan types:
          sca  - Configuration scan
          csm  - Configuration scan (same as sca)
          svm  - Software vulnerability scan
          sva  - Software vulnerability scan (same as svm)
          fim  - File integrity monitoring scan

        Returns:
            dict: Dictionary object describing last scan results

        """

        if self.scan_history_supported(scan_type) is False:
            exception_message = "Unsupported scan type: %s" % scan_type
            raise CloudPassageValidation(exception_message)
        else:
            scan_type_normalized = self.supported_scans[scan_type]
            endpoint = "/v1/servers/%s/%s" % (server_id, scan_type_normalized)
            request = HttpHelper(self.session)
            response = request.get(endpoint)
            return response

    def scan_history(self, **kwargs):
        """Get a list of historical scans.

        Keyword args:
            server_id (str): Id of server
            module (str or list): sca, fim, svm, sam
            status (str or list): queued, pending, running, completed_clean,
                completed_with_errors, failed
            since (str): ISO 8601 formatted string representing the starting
                date and time for query
            until (str): ISO 8601 formatted string representing the ending
                date and time for query
            max_pages (int): maximum number of pages to fetch.  Default: 20.

        Returns:
            list: List of scan objects
        """

        max_pages = 20
        url_params = kwargs
        if "server_id" in kwargs:
            url_params["server_id"] = kwargs["server_id"]
        if "module" in kwargs:
            url_params["module"] = self.verify_and_build_module_params(
                kwargs["module"])
        if "status" in kwargs:
            url_params["status"] = self.verify_and_build_status_params(
                kwargs["status"])
        if "max_pages" in kwargs:
            max_pages = kwargs["max_pages"]
        endpoint = self.endpoint()
        key = "scans"
        request = HttpHelper(self.session)
        params = utility.assemble_search_criteria(self.supported_search_fields,
                                                  url_params)
        response = request.get_paginated(endpoint, key, max_pages,
                                         params=params)
        return response

    def findings(self, scan_id, findings_id):
        """Get FIM, CSM, and SVA findings details by scan and findings ID

        Args:
            scan_id (str): ID of scan_id
            findings_id (str): ID of findings to retrieve

        Returns:
            dict: Dictionary object descrbing findings

        """
        sanity.validate_object_id(scan_id)
        sanity.validate_object_id(findings_id)
        endpoint = "{}/{}/findings/{}".format(self.endpoint(), scan_id,
                                              findings_id)
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        return response

    def scan_details(self, scan_id):
        """Get detailed scan information

        Args:
            scan_id (str): ID of scan

        Returns:
            dict: Dictionary object describing scan details

        """

        endpoint = "{}/{}".format(self.endpoint(), scan_id)
        request = HttpHelper(self.session)
        return request.get(endpoint)[self.object_name]

    def scan_status_supported(self, scan_status):
        """Determine if scan status is supported for query"""
        result = False
        if scan_status in self.supported_scan_status:
            result = True
        return result

    def scan_type_supported(self, scan_type):
        """Determine if scan type is supported for query"""
        result = False
        if scan_type in self.supported_scans:
            result = True
        return result

    def scan_history_supported(self, scan_type):
        """Determine if scan type is supported for historical query"""
        result = False
        if scan_type in self.supported_historical_scans:
            result = True
        return result

    def verify_and_build_status_params(self, status_raw):
        """Verifies status params and data types."""
        if isinstance(status_raw, list):
            for status in status_raw:
                if self.scan_status_supported(status) is not True:
                    exception_message = "%s is not supported" % status
                    raise CloudPassageValidation(exception_message)
        else:
            if self.scan_status_supported(status_raw) is False:
                error_message = "Unsupported status: %s" % status_raw
                raise CloudPassageValidation(error_message)
        return status_raw

    def verify_and_build_module_params(self, module_raw):
        """Verifies module params and data types"""
        if isinstance(module_raw, list):
            for module in module_raw:
                if self.scan_type_supported(module) is not True:
                    exception_message = "%s is not supported" % module
                    raise CloudPassageValidation(exception_message)
        else:
            if self.scan_type_supported(module_raw) is False:
                error_message = "Unsupported module: %s" % module_raw
                raise CloudPassageValidation(error_message)
        return module_raw
