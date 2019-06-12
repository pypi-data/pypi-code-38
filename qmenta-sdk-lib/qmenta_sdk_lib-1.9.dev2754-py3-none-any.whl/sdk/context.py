import json
import logging
import os
import re
import zipfile

import requests
import uuid
from enum import Enum

from qmenta.sdk.directory_utils import TemporaryDirectory
from qmenta.sdk.directory_utils import mkdirs


class NoFilesError(Exception):
    """ Error raised when no files are found in a `data` analysis type """

    pass


class AnalysisContext:
    class QCEntity(Enum):
        """
        Enum with the following options:
        ANALYSIS, SESSION
        """

        ANALYSIS = "analysis"
        SESSION = "patients"

    class QCStatus(Enum):
        """
        Enum with the following options:
        FAIL, PASS
        """

        PASS = "pass"
        FAIL = "fail"

    class ReplaceFlag(Enum):
        """
        Enum with the following options:
        ALL, ONLY_FILE
        """

        ONLY_FILE = "1"
        ALL = "2"

    def __init__(self, analysis_id, comm):
        """
        Context object that interfaces with the QMENTA platform. Should not be created directly.
        """
        self.analysis_id = analysis_id
        self.__comm = comm
        self.__containers_data = {}
        self.analysis_data = None
        self.parent_analysis_data = None

    def fetch_analysis_data(self):
        """
        Fetch information about current analysis.

        Returns
        -------
        dict
            Dictionary that contains important information about the current analysis, such as:
                * state (str) : State of the analysis
                * name (str) : Name of the analysis
                * script_name (str) : Name of the script
                * analysis_id (str) : A unique identifier for the current analysis
                * user_id (str) : Username of the user that started the analysis
                * patient_secret_name (str) : Name of the subject
                * ssid (str) : Timepoint identifier
                * settings (dict) : Settings dictionary. See documentation in method `get_settings`
                * tags (list) : List of tags
                * version (str) : Tool version
        """
        res = self.__comm.send_request("analysis_manager/get_analysis_list", {"id": self.analysis_id})
        if res:
            self.analysis_data = res[0]
            self.analysis_data["analysis_id"] = str(self.analysis_id)
            return self.analysis_data
        else:
            error_msg = "Analysis with ID={} not found".format(self.analysis_id)
            raise ValueError(error_msg)

    def fetch_parent_analysis_data(self):
        """
        Fetch information about the parent analysis of the current analysis.

        Returns
        -------
        dict
            Dictionary that contains important information about the current analysis, such as:
                * state (str) : State of the analysis
                * name (str) : Name of the analysis
                * script_name (str) : Name of the script
                * user_id (str) : Username of the user that started the analysis
                * patient_secret_name (str) : Name of the subject
                * ssid (str) : Timepoint identifier
                * settings (dict) : Settings dictionary. See documentation in method `get_settings`
                * tags (list) : List of tags
                * version (str) : Tool version
        """

        if self.parent_analysis_data is not None:
            return self.parent_analysis_data

        if not self.has_parent_analysis():
            raise Exception("The current analysis does not have parent analysis !")

        parent_analysis_id = self.analysis_data["super_analysis"]["parent_analysis_id"]

        res = self.__comm.send_request("analysis_manager/get_analysis_list", {"id": parent_analysis_id})
        if res:
            self.parent_analysis_data = res[0]

            # fetching the full state of a flow
            res_state = self.__comm.send_request(
                "analysis_manager/get_super_analysis_state", {"analysis_id": parent_analysis_id}
            )

            self.parent_analysis_data["nodes"] = res_state.get("data", dict()) if res_state else dict()

            return self.parent_analysis_data
        else:
            error_msg = "Analysis flow with ID={} not found".format(parent_analysis_id)
            raise ValueError(error_msg)

    def get_communication_object(self):
        """
        Return the communication object used for communication with the platform

        Returns
        -------
        CommunicationObject
            The communication object used to communicate the platform
        """
        return self.__comm

    def set_qc_status(self, status=QCStatus.PASS, comments="", entity=QCEntity.ANALYSIS, input_id=None):
        """
        Changes the analysis or session QC status.

        Parameters
        ----------
        status : QCStatus
            QCStatus.PASS or QCStatus.FAIL
        comments : str, optional
            Additional comments explaining why the QC status has been set to pass or fail.
        entity : QCEntity, optional
            QCEntity.ANALYSIS or QCEntity.SESSION
        input_id : str, optional
            The id of the session in the settings definition when entity is QCEntity.SESSION
        """
        logger = logging.getLogger(__name__)

        if entity == self.QCEntity.ANALYSIS:
            item_id = self.analysis_id
        elif entity == self.QCEntity.SESSION:
            container_id = self.analysis_data["settings"][input_id]["container_id"]
            res = self.__comm.send_request("file_manager/get_container_files", {"container_id": container_id})
            item_id = str(int(res["patient_id"]))
        else:
            raise RuntimeError("Unknown entity {}".format(entity))

        data_to_send = {"item_ids": item_id, "status": status.value, "comments": comments, "entity": entity.value}

        logger.info("Setting ({}={}) QC status to {}: {}".format(entity.name, item_id, status, comments))

        res = self.__comm.send_request("projectset_manager/set_qa_status", data_to_send)
        if not res["success"]:
            raise RuntimeError(res["error"])

    def download_session_qa_requirements(self, path):
        """
        Downloads the list of project-level requirements for a session.

        Parameters
        ----------
        path : str
            The location where to store the requirements.r
        """
        logger = logging.getLogger(__name__)

        if os.path.exists(path):
            raise RuntimeError("Cannot download session qa because {} already exists!".format(path))

        data_to_send = {"project_id": self.analysis_data["projectset_id"]}

        url = "projectset_manager/get_session_qa_requirements"
        res = self.__comm.send_request(url, data_to_send)
        if not res["success"]:
            raise RuntimeError("Cannot download the session QA requirements")
        else:
            logger.info("Storing project-level session QA requirements at {}".format(path))
            with open(path, "w") as fs:
                # Process as JSON to validate
                json.dump(res["data"], fs)

    def upload_session_qa_report(self, input_id, path):
        """
        Sets the QA status for all the files of session as per requirements

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        path : str
            The json file with the QA status for all files and rules
        """
        logger = logging.getLogger(__name__)

        with open(path, "r") as fp:
            # Load as JSON to verify structure
            data = json.loads(fp.read())

        container_id = self.analysis_data["settings"][input_id]["container_id"]
        data_to_send = {"container_id": container_id, "data": json.dumps(data)}
        logger.info(
            "Sending session QA report with id {}:\n{}".format(data_to_send["container_id"], data_to_send["data"])
        )

        res = self.__comm.send_request("file_manager/set_session_qa", data_to_send)
        if not res["success"]:
            raise RuntimeError(res["error"])

    def set_progress(self, message=None, value=None):
        """
        Sets analysis progress.

        Parameters
        ----------
        value : int, optional
            Number between 0 and 100 indicating the current status of the execution
        message : str, optional
            Progress message.
        """
        logger = logging.getLogger(__name__)

        if not value and not message:
            logger.warning("No information is available to report the progress")
            return

        data_to_send = {"analysis_id": self.analysis_id}

        if value:
            value = int(value)  # Cast to int to avoid float/string problems
            if value > 100:
                logger.warning("The progress value should be between 0 and 100 (using 100 instead)")
                value = 100
            elif value < 0:
                logger.warning("The progress value should be between 0 and 100 (using 0 instead)")
                value = 0
            data_to_send["value"] = value

        if message:
            data_to_send["message"] = message

        logger.info("Progress: {} -> {}".format(value, message))
        self.__comm.send_request("analysis_manager/set_analysis_progress", data_to_send)

    def get_settings(self):
        """
        Analysis settings.

        Returns
        -------
        dict
            Settings for the current analysis. This includes all the parameters defined in the tool specification
            (checkboxes, input fields, etc.) and can be accessed using their identifier.
        """
        return self.analysis_data["settings"]

    def get_files(
        self,
        input_id,
        modality=None,
        tags=None,
        reg_expression=None,
        file_filter_condition_name=None,
        subject_container_id=None,
    ):
        """
        Returns the files in the input container specified by `input_id` that match the modality, tags
        and regular expression, if any. (X)OR that are selected by the file filter condition
        defined in the tool settings.

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        modality : str, optional
            Optional modality, will allow any modalities if None given.
            Default is None.
        tags : set, optional
            Optional set of tags, will allow any tags if None given, and will match any set of tags (including
            the empty set) otherwise.
            Default is None.
        reg_expression : str, optional
            Regular expression to match with the file names in the specified container, will allow any file names
            if None given.
            Default is None.
        file_filter_condition_name : str, optional
            File filter specified in the settings of the tool.
            Default is None.

        Examples
        --------

        Get all files that passed c_TEST (including any selection the user may have done using the GUI)

        >>> context.get_files('input', file_filter_condition_name='c_TEST')

        Get all files that passed c_TEST and have no tags

        >>> context.get_files('input', file_fitler_condition_name='c_TEST', tags=set()

        Get all files that passed c_TEST and have the DTI tag in their list of tags

        >>> context.get_files('input', file_fitler_condition_name='c_TEST', tags={'DTI'})

        Get all files that passed c_TEST whose name match the given regexp

        >>> context.get_files('input', file_filter_condition_name='c_TEST', reg_expression='^some_expression[0-9]')

        Alternatively, you can use no file_filter_condition_name to browse through the whole input container

        >>> context.get_files('input')

        Returns
        -------
        list of qmenta.sdk.context.File
            List of selected file handlers from the container.
        """
        logger = logging.getLogger(__name__)
        logger.info("Get files: {} [modality={} / tags={} / regex={}]".format(input_id, modality, tags, reg_expression))

        file_filter_condition_name = file_filter_condition_name or ""

        input_settings = self.analysis_data["settings"][input_id]
        is_subject_setting = "containers" in input_settings
        container_id = subject_container_id if is_subject_setting else input_settings["container_id"]

        if is_subject_setting and subject_container_id is None:
            msg = "must define subject_container_id for subjects with multiple sessions"
            logger.error(msg)
            raise Exception(msg)

        if is_subject_setting:
            # get input settings for correct container
            try:
                all_input_setting = [r for r in input_settings["containers"] if r["container_id"] == container_id]
                input_settings = all_input_setting[0]
            except KeyError:
                msg = "container {} not found for input {!r}".format(container_id, input_id)
                logger.exception(msg)
                raise Exception(msg)

            # ensure data structure is compatible with expected data
            if input_id not in self.__containers_data:
                self.__containers_data[input_id] = {}

            have_container_data = container_id in self.__containers_data[input_id]

        else:
            have_container_data = input_id in self.__containers_data

        if not have_container_data:
            # If files from the file container are not available, fetch them
            res = self.__comm.send_request("file_manager/get_container_files", {"container_id": container_id})

            if is_subject_setting:
                self.__containers_data[input_id][container_id] = res["data"]
            else:
                self.__containers_data[input_id] = res["data"]

        container_data_to_work_with = self.__containers_data[input_id]
        if is_subject_setting:
            container_data_to_work_with = self.__containers_data[input_id][container_id]

        if file_filter_condition_name:
            # Get the files that passed the file_filter and take those that have the required conditions

            selected_files = []

            if input_settings["passed"]:
                try:
                    file_filter_spec = input_settings["filters"][file_filter_condition_name]
                except KeyError:
                    msg = "File filter condition {} not specified in the container {} settings !".format(
                        file_filter_condition_name, input_id
                    )
                    logger.error(msg)
                    raise Exception(msg)

                for file_desc in file_filter_spec["files"]:
                    metadata = container_data_to_work_with["meta"]
                    find_file_data = [f for f in metadata if f["name"] == file_desc["name"]]
                    if find_file_data:
                        file_data = find_file_data[0]

                        fname, fmetadata, ftags = file_data["name"], file_data["metadata"], set(file_data["tags"])

                        if _should_include_file(
                            fname, fmetadata.get("modality", None), ftags, modality, tags, reg_expression
                        ):
                            selected_files.append(File(container_id, fname, fmetadata, ftags, self.__comm))

            return selected_files
        else:
            # in case the file filter condition name is not specified then we need to take the other
            # concrete search conditions i.e. modality, tags, reg_expression

            # filter the files according to the filter defined
            return self.__files_from_container_data(
                container_data_to_work_with, container_id, modality, tags, reg_expression
            )

    def _get_files_from_container(self, container_id, modality=None, tags=None, reg_expression=None):
        logger = logging.getLogger(__name__)
        logger.info("Get files from container {}".format(container_id))
        res = self.__comm.send_request("file_manager/get_container_files", {"container_id": container_id})
        if res["success"]:
            return self.__files_from_container_data(res["data"], container_id, modality, tags, reg_expression)
        else:
            raise RuntimeError(res["error"])

    def __files_from_container_data(self, container_data, container_id, modality, tags, reg_expression):
        selected_files = []
        for file_data in container_data["meta"]:

            # TODO: Here we are assuming that file metadata has a name and a metadata attribute. Need of jsonschema

            fname, fmetadata, ftags = file_data["name"], file_data["metadata"], set(file_data["tags"])
            assume_file_selected = _should_include_file(
                fname, fmetadata.get("modality", None), ftags, modality, tags, reg_expression
            )

            if assume_file_selected:
                selected_files.append(File(container_id, fname, fmetadata, ftags, self.__comm))
        return selected_files

    @staticmethod
    def __detect_file_format(file_path):
        if file_path.endswith(".nii"):
            return "nifti"
        elif file_path.endswith(".nii.gz"):
            return "nifti"
        elif file_path.endswith(".bvec"):
            return "bvec"
        elif file_path.endswith(".bval"):
            return "bval"
        else:
            return None

    def new_scan_session(
        self, ssid=None, date_at_scan=None, age_at_scan=None, backup_age=None, patient_metadata_id=None
    ):
        """
        Add a new scan session. Only functional for analysis tools of type `data`.

        Parameters
        ----------
        ssid : int, optional
        date_at_scan : str, optional
            Possible formats: '%d.%m.%Y' / '%Y-%m-%d'. Examples: '01.01.2000' / '2000-01-01'
        age_at_scan : int, optional
        backup_age : int, optional
        patient_metadata_id : int, optional

        Returns
        -------
        int
            ID of the new scan session
        """
        try:
            patient_secret_name = self.analysis_data["patient_secret_name"]
        except KeyError:
            raise RuntimeError("Patient secret name not available in analysis information. Check platform failures.")
        try:
            md5_original_file = self.get_settings()["md5_original_file"]
        except KeyError:
            raise RuntimeError("MD5 hash not available via analysis settings. Check platform failures.")

        data = {
            "patient_secret_name": patient_secret_name,
            "md5_original_file": md5_original_file,
            "date_at_scan": date_at_scan,
            "age_at_scan": age_at_scan,
            "backup_age": backup_age,
            "analysis_id": self.analysis_id,
        }

        if ssid is not None:
            data["ssid"] = ssid

        if patient_metadata_id:
            data["patient_metadata_id"] = patient_metadata_id

        reply = self.__comm.send_request("patient_manager/add_scan_session", data)

        if reply["success"]:
            return reply["data"]
        else:
            raise Exception(reply["error"])

    def upload_file(
        self,
        source_file_path,
        destination_path,
        modality=None,
        tags=None,
        file_info=None,
        file_format=None,
        protocol=None,
        container_id=None,
        replace=None,
    ):
        """
        Upload a file to the platform, to be part of the result files.

        Parameters
        ----------
        source_file_path : str
            Path to the file to be uploaded.
        destination_path : str
            Path in the output container. Will be shown in the platform.
        modality: str, optional
            Optional modality of the uploaded file.
            None by default.
        tags : set, optional
            Set of tags for the uploaded file.
            None by default.
        file_info : dict, optional
            File information metadata.
        file_format : str, optional
            Use "dicom" when .zip file with .dcm slices (uplading a "nifti" file is automatically recognized as such).
        """
        logger = logging.getLogger(__name__)

        tags = tags or set()

        if modality:
            tags.add("m:" + modality)

        logger.info("Uploading {!r} to {!r}".format(source_file_path, destination_path))

        # File information
        file_name = destination_path.split("/")[-1]
        total_bytes = os.path.getsize(source_file_path)
        session_id = str(uuid.uuid4())
        if total_bytes > 0:
            logger.debug(
                "Uploading file {} with size {} bytes and session ID {}".format(
                    source_file_path, total_bytes, session_id
                )
            )
        else:
            logger.warning("Skipping empty file {} upload".format(source_file_path))
            return

        # Try to find a proper file format when not available
        file_format = file_format or self.__detect_file_format(source_file_path)

        # Try to find a proper protocol when not available
        protocol = protocol or file_name.split(".")[0] if "." in file_name else file_name

        # making chunks of the file and sending one by one
        response = False
        chunk_num = 0
        with open(source_file_path, "rb") as file_object:
            data = file_object.read(self.__comm.chunk_size)
            # If chunck num is 0, we still want to send an empty file
            while data or chunk_num == 0:
                start_position = chunk_num * self.__comm.chunk_size
                end_position = start_position + self.__comm.chunk_size - 1
                bytes_to_send = self.__comm.chunk_size

                if end_position >= total_bytes:
                    end_position = total_bytes - 1
                    bytes_to_send = total_bytes - chunk_num * self.__comm.chunk_size

                bytes_range = "bytes {}-{}/{}".format(start_position, end_position, total_bytes)

                # Request headers
                req_headers = dict()
                req_headers["Content-Type"] = "application/octet-stream"
                req_headers["Content-Range"] = bytes_range
                req_headers["Session-ID"] = str(session_id)
                req_headers["Content-Length"] = str(bytes_to_send)
                req_headers["Content-Disposition"] = "attachment; filename={}".format(file_name)

                # If it is the last chunk, define more header fields
                if chunk_num * self.__comm.chunk_size + bytes_to_send == total_bytes:
                    logger.debug("Sending last data chunk")
                    req_headers["X-Mint-Analysis-Output"] = str(self.analysis_id)
                    req_headers["X-Mint-File-Destination-Path"] = destination_path
                    req_headers["X-Mint-File-Tags"] = ",".join(tags)
                    if file_info:
                        req_headers["X-Mint-File-Info"] = json.dumps(file_info)
                    if file_format:
                        req_headers["X-Mint-File-Format"] = str(file_format)
                    if protocol:
                        req_headers["X-Mint-Protocol"] = str(protocol)
                    if container_id:
                        req_headers["X-Mint-Container"] = str(container_id)
                    if replace:
                        assert isinstance(replace, AnalysisContext.ReplaceFlag)
                        req_headers["X-Mint-Replace-Flag"] = replace.value
                    req_headers["X-Requested-With"] = "XMLHttpRequest"

                response = self.__comm.send_request("upload", data, req_headers, return_json=False)

                # Read next chunk
                data = file_object.read(self.__comm.chunk_size)
                chunk_num += 1

            # Verify that file has been indeed saved into the platform
            if response and json.loads(response.text)["success"]:
                logger.info("Upload completed")
            else:
                msg = "File {} could not be uploaded to the platform".format(source_file_path)
                logger.error(msg)
                raise RuntimeError(msg)

    def download_resource(self, resource_path, destination_path):
        """
        Downloads a file from the user/group tool resources. The resource path can include subdirectories and must
        be relative:

        >>> context.download_resource('dir/subdir/file.nii.gz', '/root/file.nii.gz')

        Parameters
        ----------
        path : str
            Path to the file in the resources bucket.
        destination_file_path : str
            Path where the file will be downloaded.
        """

        self._download_resource(resource_path, destination_path, type="tool_resource")

    def _download_resource(self, path, destination_file_path, type="template"):
        """
        Downloads a resource file from the bucket (user/group based resources, or legacy).

        Parameters
        ----------
        path : str
            Path to the file in the resources bucket.
        destination_file_path : str
            Path where the file will be downloaded.
        type : str
            The resource type
        """
        logger = logging.getLogger(__name__)
        logger.info("Downloading resource {!r} to {!r}".format(path, destination_file_path))

        data_to_send = {"analysis_id": self.analysis_id, "type": type, "path": path}
        try:
            res = self.__comm.send_request(
                "analysis_manager/get_resource", data_to_send, total_retry=1, return_json=False, stream=True
            )
        except requests.HTTPError as ex:
            logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Resource file {!r} not found".format(path)
                logger.error(msg)
                raise Exception(msg)

            raise

        mkdirs(os.path.dirname(destination_file_path))

        logger.debug("Saving {!r}".format(destination_file_path))
        with open(destination_file_path, "wb") as fp:
            for chunk in res.iter_content(chunk_size=self.__comm.chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()
        logger.debug("Finished downloading resource {!r}".format(destination_file_path))

    def _get_manual_analysis_data(self):
        """
        Returns a dictionary with the manual analysis data generated during the manual step (user interaction)

        Returns
        -------
        dict
            The values generated during the manual step.
        """
        logger = logging.getLogger(__name__)
        logger.info("Getting manual analysis data")

        data_to_send = {"analysis_id": self.analysis_id}
        try:
            res = self.__comm.send_request("analysis_manager/get_manual_analysis_data", data_to_send, total_retry=1)
        except requests.HTTPError as ex:
            logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Manual analysis data not found (request exception)"
                logger.error(msg)
                raise Exception(msg)
            raise
        else:
            return res["value"]

    def set_metadata_value(self, key, value, title=None, readonly=False):
        """
        Sets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.
        value : int, ,str, float or list
            The new content of the parameter.
        title : str, optional
            How the metadata field should be presented
        readonly : bool, optional
            Whether the user should be able to edit the value on the platform or not (only by analyses)
        """
        logger = logging.getLogger(__name__)

        assert isinstance(key, str)
        assert isinstance(value, (int, list, str, float))

        if not self._get_metadata_value(key):
            # Create the metadata field if it does not exist
            if title:
                assert isinstance(title, str)

            allowed_types = {int: "integer", list: "list", str: "string", float: "decimal"}

            if type(value) not in allowed_types:
                raise ValueError("Invalid type for the metadata value: {!r}".format(type(value)))
            parameter_type = allowed_types[type(value)]
            self._assure_metadata_parameters(
                [{"key": key, "title": title if title else key, "type": parameter_type, "readonly": int(readonly)}]
            )

        logger.info("Setting metadata parameter: {} = {!r}".format(key, value))
        self._set_metadata_value(key, value)

    def _set_metadata_value(self, key, value, patient_secret_name=None, ssid=None):
        """
        Sets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.
        value : int, str, float
            The new content of the parameter.
        patient_secret_name : str
            Manually select the patient_secret_name (only for upload analysis)
        ssid : str
            Manually select the ssid (only for upload analysis)
        """
        logger = logging.getLogger(__name__)

        subject_name = self.analysis_data["patient_secret_name"]
        if patient_secret_name:
            subject_name = patient_secret_name

        session_id = self.analysis_data["ssid"]
        if ssid:
            session_id = ssid

        data_to_send = {
            "analysis_id": self.analysis_id,
            "key": key,
            "value": value,
            "patient_secret_name": subject_name,
            "ssid": session_id,
        }

        try:
            res = self.__comm.send_request("analysis_manager/set_metadata_value", data_to_send, total_retry=1)
            if not res["success"]:
                msg = "Metadata error: {!r}".format(res["error"])
                logger.error(msg)
                raise Exception(msg)
        except requests.HTTPError as ex:
            logger.exception(ex)
            raise

    def get_metadata_value(self, key):
        """
        Gets the value of a metadata parameter for the current session

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.

        Returns
        -------
        The value of the parameter if it exists, None otherwise
        """
        logger = logging.getLogger(__name__)
        logger.info("Getting metadata value: {}".format(key))
        return self._get_metadata_value(key)

    def _get_metadata_value(self, key):
        """
        Gets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.

        Returns
        -------
        The value of the parameter
        """
        logger = logging.getLogger(__name__)

        data_to_send = {
            "analysis_id": self.analysis_id,
            "ssid": self.analysis_data["ssid"],
            "patient_secret_name": self.analysis_data["patient_secret_name"],
        }

        if key is not None:
            data_to_send["key"] = key

        try:
            res = self.__comm.send_request("analysis_manager/get_metadata_value", data_to_send, total_retry=1)
            if not res["success"]:
                if "error" in res and "no metadata field" in res["error"]:
                    # The metadata field does not exist => return None
                    return None
                else:
                    msg = "Metadata error: {!r}".format(res["error"])
                    logger.error(msg)
                    raise RuntimeError(msg)
        except requests.HTTPError as ex:
            logger.exception(ex)
            raise
        else:
            return res["value"]

    def _assure_metadata_parameters(self, params):
        """
        Ensure that a parameter exists.

        Parameters
        ----------
        params : list
            The definition of the parameter. It may contain "title", "type", "visible", "readonly" or "order".
        """
        logger = logging.getLogger(__name__)

        if not isinstance(params, list):
            params = list(params)

        for data_to_send in params:
            if not isinstance(data_to_send, dict):
                msg = "Format error. Metadata param configuration should be stored in a dictionary"
                logger.error(msg)
                raise TypeError(msg)

            data_to_send["analysis_id"] = self.analysis_id
            logger.info("Checking metadata param config: {}".format(data_to_send))
            try:
                res = self.__comm.send_request("analysis_manager/set_metadata_param", data_to_send, total_retry=1)
                if not res["success"]:
                    msg = "Metadata error: {!r}".format(res["error"])
                    logger.error(msg)
                    raise Exception(msg)
            except requests.HTTPError as ex:
                logger.exception(ex)
                raise

    # For multi-timepoint (longitudinal) analyses
    def get_sessions(self, input_id):
        input_data = self.analysis_data["settings"][input_id]
        try:
            containers = input_data["containers"]
        except KeyError:
            msg = "settings for {!r} must be from a subject"
            logging.getLogger(__name__).error(msg)
            raise Exception(msg)
        else:
            return [Container(self, input_id, container_data) for container_data in containers]

    def has_parent_analysis(self):
        return "super_analysis" in self.analysis_data

    def get_parent_file_selection(self, input_id):

        if not self.has_parent_analysis():
            raise Exception("The current analysis does not have parent analysis !")

        container_id = int(self.analysis_data.get("settings", dict()).get(input_id, dict()).get("container_id", 0))
        if container_id == 0:
            raise Exception("No input container was selected for {} !".format(input_id))

        parent_data_settings = self.fetch_parent_analysis_data().get("settings", dict())

        selected_files = set()

        for setting_value in parent_data_settings.values():
            if not isinstance(setting_value, dict):
                continue

            setting_container_id = int(setting_value.get("container_id", 0))
            setting_passed = setting_value.get("passed", False)

            if (setting_container_id == container_id) and setting_passed:
                for filter in setting_value.get("filters", dict()).values():
                    if not filter["passed"]:
                        continue
                    selected_files.update([ff["name"] for ff in filter.get("files", [])])

        return list(selected_files)

    def set_analysis_output_variables(self, variables_dict, clear_previous=False):
        """
        Sets the output variables of analysis

        Parameters
        ----------
        variables_dict : str
            Dictionary with the output variables
        clear_previous : bool, optional
            Whether the previous output variables should be cleared or not
        """
        logger = logging.getLogger(__name__)

        if not isinstance(variables_dict, dict):
            logger.error(
                "The output variables are not of type dictionary ! (actual type {})".format(str(type(variables_dict)))
            )
            raise RuntimeError("The output variables are not of type dictionary !")

        variables_to_send = json.dumps(variables_dict)

        try:
            data_to_send = {"output": variables_to_send, "clear": int(clear_previous), "analysis_id": self.analysis_id}

            res = self.__comm.send_request("analysis_manager/set_output_variables", data_to_send, total_retry=2)
            if not res["success"]:
                msg = "Setting output variables: {!r}".format(res["error"])
                logger.error(msg)
                raise Exception(msg)
        except requests.HTTPError as ex:
            logger.exception(ex)
            raise


class Container:
    # is a kind of session, no other kinds of session currently implemented

    def __init__(self, context, input_id, container_data):
        self.__container_id = container_data.get("container_id", None)
        self.__input_id = input_id
        self.__context = context

        self.container_data = container_data

    def get_metadata(self):
        return self.__context._get_metadata_value(None)

    def get_files(self, modality=None, tags=None, reg_expression=None, file_filter_condition_name=None):
        return self.__context.get_files(
            self.__input_id, modality, tags, reg_expression, file_filter_condition_name, self.__container_id
        )

    def _set_metadata_value(self, key, value):
        return self.__context._set_metadata_value(
            key, value, self.container_data["subject_name"], self.container_data["ssid"]
        )


class File:
    def __init__(self, container_id, name, metadata, tags, comm):
        """
        Object that represents a file and all its metadata in the platform. Should not be created directly.
        """
        self.__comm = comm
        self.__container_id = container_id
        self.name = name
        self.__metadata = metadata
        self.__tags = tags
        self.__download_path = None

    def get_file_modality(self):
        """
        Get the modality of the file.

        Returns
        -------
        str or None
            Modality of the file or None if not known.
        """
        return self.__metadata.get("modality", None)

    def get_file_format(self):
        """
        Get the format of the file (e.g. 'nifti', 'txt', etc.).

        Returns
        -------
        str
            File format or None if not known.
        """
        return self.__metadata.get("format", None)

    def get_file_info(self):
        """
        Get the file information. The type of information depends on the type of file
        (e.g. nifti files include information such as 'Data strides', 'Data type', 'Dimensions' or 'Voxel size').

        Returns
        -------
        dict
            Dictionary of key-value pairs that depend on the format of the file.
        """
        return self.__metadata.get("info", {})

    def get_file_tags(self):
        """
        Get the file tags.

        Returns
        -------
        set
            Set of tags associated to this file
        """
        return self.__tags if self.__tags is not None else set()

    def get_file_path(self):
        """
        Get the file download path.

        Returns
        -------
        str
            The path of the file where it has been downloaded

        Raises
        ------
        RuntimeError
            If `get_file_path` is called before the file has been downloaded
        """
        if self.__download_path is None:
            err_msg = "File {!r} has no path because it has not been downloaded".format(self.name)
            logging.getLogger(__name__).error(err_msg)
            raise RuntimeError(err_msg)
        else:
            return self.__download_path

    def __download_file(self, destination_file_path):
        """
        Downloads the file into the specified `destination_file_path`.

        Parameters
        ----------
        destination_file_path : str
            Path where the file should be downloaded.
        """
        source_file = self.name

        logger = logging.getLogger(__name__)
        logger.info("Downloading {!r} to {!r}".format(source_file, destination_file_path))

        data_to_send = {"container_id": self.__container_id, "files": source_file}
        logger.debug("Accessing {files!r} from container {container_id!r}".format(**data_to_send))
        res = self.__comm.send_request("file_manager/download_file", data_to_send, return_json=False, stream=True)

        mkdirs(os.path.dirname(destination_file_path))

        with open(destination_file_path, "wb") as fp:
            for chunk in res.iter_content(chunk_size=self.__comm.chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()

        self.__download_path = destination_file_path
        logger.debug("Finished downloading {!r}".format(destination_file_path))

    def download(self, dest_path, unpack=True):
        """
        Downloads a file or the contents of a packed file to to the specified `path`.

        Parameters
        ----------
        dest_path:
            Path where the file should be downloaded to.
        unpack:
            Tells the function whether the file should be unpacked to the given folder.

        Returns
        -------
        str:
            The full path of the file or the folder with the unpacked files.
        """
        logger = logging.getLogger(__name__)
        source_file = self.name

        # Normalize path
        dest_path = os.path.abspath(dest_path)

        logger.debug("Using path {!r}".format(dest_path))

        if source_file.endswith(".zip") and unpack:
            # Download the zip to a temporary directory and unpack its contents to the user dir path
            with TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, source_file)
                self.__download_file(temp_path)
                with zipfile.ZipFile(temp_path, "r") as zip_ref:
                    file_list = zip_ref.namelist()
                    logger.info("Decompressing {!r} to {!r}".format(file_list, dest_path))
                    mkdirs(dest_path)
                    zip_ref.extractall(path=dest_path)

            self.__download_path = dest_path  # Replace download path with directory
            return dest_path

        # Download the file to the directory and return the full path
        else:
            destination_file_path = os.path.join(dest_path, source_file)
            self.__download_file(destination_file_path)
            return destination_file_path


""" HELPERS """


def _should_include_file(fname, fmodality, ftags, search_modality, search_tags, search_reg_expression):
    # Checks if file should be selected or not according to the specified selectors.

    assert fname

    if search_modality is not None and fmodality != search_modality:
        return False

    # Search with tags has three outcomes:
    # 1. None - No filter (take all)
    # 2. Empty set - Take only those with no tags
    # 3. Set with elements - Take those with AT LEAST those tags
    if search_tags is not None:
        assert isinstance(ftags, set)
        assert isinstance(search_tags, set)
        if search_tags == set() and ftags != set():
            return False
        elif not search_tags.issubset(ftags):
            return False

    # If regexp, filter with it
    if search_reg_expression is not None:
        if not re.match(search_reg_expression, fname):
            return False

    return True
