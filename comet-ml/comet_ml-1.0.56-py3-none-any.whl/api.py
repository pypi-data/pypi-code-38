# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed
#  without the express permission of Comet ML Inc.
# *******************************************************

import copy
import logging
import six
import re

import requests

from .comet import get_api_key, get_rest_api_key
from .config import get_config
from .connection import get_backend_session
from .experiment import BaseExperiment

LOGGER = logging.getLogger(__name__)


def _get_server_url():
    """
    Get the base URL from the config
    """
    url = get_config("comet.url_override")
    ## just get the https://address portion:
    return "/".join(url.split("/", 3)[0:3])


class MetricsList(list):
    def __getitem__(self, item):
        if isinstance(item, int):
            return super(MetricsList, self).__getitem__(item)
        else:
            return [
                (x["step"], float(x["metricValue"]))
                for x in self
                if x["metricName"] == item
            ]


class APIExperiment(object):
    """
    The APIExperiment class is used to access data from the
    Comet.ml REST API.

    You can use an instance of the APIExperiment() class to easily
    access all of your logged experiment information
    at [Comet.ml](https://www.comet.ml), including metrics, parameters,
    images, tags, and assets.

    ```
    >>> import comet_ml
    >>>> comet_api = comet_ml.API()

    ## Get an APIExperiment:
    >>>  experiment = comet_api.get("cometpublic/comet-notebooks/example 001")

    ## Get metrics:
    >>> experiment.metrics_raw["train_accuracy"]

    ## Get the `ExistingExperiment`:
    >>> exp = comet_ml.ExistingExperiment(experiment.key)
    ```

    Note that the data received from API.get() is cached. To reset
    the cache, create a new API() instance.

    For more usage examples, see [Comet REST examples](../Comet-REST-API/).
    """

    def __init__(self, api, workspace, project, experiment):
        """
        REST API Experiment interface.
        """
        self._api = api
        self.workspace = workspace
        self.project = project
        if isinstance(experiment, APIExperiment):
            experiment_key = experiment.key
        else:
            experiment_key = experiment
        self._api._build_cache(self.workspace, self.project, experiment_key)
        self.key = self._api._get(self.workspace, self.project, experiment_key)[
            "experiment_key"
        ]

    def _get_experiment_url(self):
        return "%s/%s/%s/%s" % (
            self._api.get_url_server(),
            self.workspace,
            self.project,
            self.key,
        )

    ## Just steal these two methods for now:
    _in_jupyter_environment = BaseExperiment._in_jupyter_environment
    display = BaseExperiment.display

    @property
    def name(self):
        """
        The name of the experiment, or None
        """
        return None if "_name" not in self.data else self.data["_name"]

    @property
    def data(self):
        """
        The experiment data in JSON-like format.
        """
        data = self._api._get(self.workspace, self.project, self.key)
        if "metrics" not in data:
            data["metrics"] = [x["name"] for x in self.metrics]
        if "_other" not in data:
            data["_other"] = self._api.get_experiment_other(self.key)
            data["other"] = [x["name"] for x in data["_other"]]
            names = [x["valueCurrent"] for x in data["_other"] if x["name"] == "Name"]
            if len(names) > 0:
                new_data = copy.deepcopy(data)
                new_data["is_key"] = False
                self._api._set(self.workspace, self.project, names[0], new_data)
                data["_name"] = names[0]
        if "parameters" not in data:
            data["parameters"] = [x["name"] for x in self.parameters]
        if "tags" not in data:
            data["tags"] = self.tags
        return data

    def __repr__(self):
        data = self._api._get(self.workspace, self.project, self.key)
        return "<APIExperiment '%s/%s/%s'>" % (
            self.workspace,
            self.project,
            data["_name"] if "_name" in data else self.key,
        )

    @property
    def html(self):
        """
        Get the HTML associated with this experiment. Not cached.
        """
        return self._api.get_experiment_html(self.key)

    @property
    def code(self):
        """
        Get the associated source code for this experiment. Not cached.
        """
        return self._api.get_experiment_code(self.key)

    @property
    def stdout(self):
        """
        Get the associated standard output for this experiment. Not cached.
        """
        return self._api.get_experiment_stdout(self.key)

    @property
    def installed_packages(self):
        """
        Get the associated installed packages for this experiment. Not cached.
        """
        return self._api.get_experiment_installed_packages(self.key)

    @property
    def os_packages(self):
        """
        Get the associated installed packages for this experiment. Not cached.
        """
        return self._api.get_experiment_os_packages(self.key)

    @property
    def graph(self):
        """
        Get the associated graph/model description for this
        experiment. Not cached.
        """
        return self._api.get_experiment_graph(self.key)

    @property
    def images(self):
        """
        Get the associated image data for this experiment. Not cached.

        The image data comes as a dictionary with the following
        keys:

            apiKey
            runId
            experimentKey
            projectId
            figCounter
            figName
            step
            runContext
            fileName
            imagePath
        """
        return self._api.get_experiment_images(self.key)

    @property
    def tags(self):
        """
        Get the associated tags for this experiment. Not cached.
        """
        return self._api.get_experiment_tags(self.key)

    @property
    def parameters(self):
        """
        Get the asssociated parameters for this experiment. Not cached.
        """
        return self._api.get_experiment_parameters(self.key)

    @property
    def metrics(self):
        """
        Get the asssociated metrics for this experiment. Not cached.
        """
        return self._api.get_experiment_metrics(self.key)

    @property
    def other(self):
        """
        Get the asssociated other items (things logged with `log_other`)
        for this experiment. Cached.
        """
        data = self._api._get(self.workspace, self.project, self.key)
        if "_other" not in data:
            data["_other"] = self._api.get_experiment_other(self.key)
            data["other"] = [x["name"] for x in data["_other"]]
            names = [x["valueCurrent"] for x in data["_other"] if x["name"] == "Name"]
            if len(names) > 0:
                new_data = copy.deepcopy(data)
                new_data["is_key"] = False
                self._api._set(self.workspace, self.project, names[0], new_data)
                data["_name"] = names[0]
        return data["_other"]

    @property
    def metrics_raw(self):
        """
        Get the asssociated raw metrics for this experiment. Not cached.
        """
        return MetricsList(self._api.get_experiment_metrics_raw(self.key))

    @property
    def git_metadata(self):
        """
        Get the asssociated git-metadata for this experiment. Not cached.
        """
        return self._api.get_experiment_git_metadata(self.key)

    @property
    def git_patch(self):
        """
        Get the asssociated git-patch for this experiment. Not cached.
        """
        return self._api.get_experiment_git_patch(self.key)

    @property
    def asset_list(self):
        """
        Get the asssociated asset-list for this experiment. Not cached.
        """
        return self._api.get_experiment_asset_list(self.key)

    def get_asset(self, asset_id, return_type="binary"):
        """
        Get an asset from this experiment. Not cached.

        Arguments:
            asset_id: the asset ID (see `APIExperiment.asset_list`)
            return_type: the type of object returned. Default is
                "binary". Options: "binary" or "text"
        """
        return self._api.get_experiment_asset(
            self.key, asset_id, return_type=return_type
        )

    def upload_asset(self, filename, step=None, overwrite=None, context=None):
        """
        Upload an asset to this experiment.
        """
        return self._api.upload_asset(
            self.key, filename=filename, step=step, overwrite=overwrite, context=context
        )

    def upload_image(
        self, filename, image_name=None, step=None, overwrite=None, context=None
    ):
        """
        Upload an image to this experiment.
        """
        return self._api.upload_image(
            self.key,
            filename=filename,
            image_name=image_name,
            step=step,
            overwrite=overwrite,
            context=context,
        )


class APIExperiments(object):
    def __init__(self, api, workspace, project):
        self._api = api
        self.workspace = workspace
        self.project = project
        self._api._build_cache(self.workspace, self.project)

    @property
    def data(self):
        """
        The project data in JSON format.
        """
        return self._api._get(self.workspace, self.project)

    def __getitem__(self, item):
        if isinstance(item, int):
            return APIExperiment(
                self._api, self.workspace, self.project, list(self)[item]
            )
        try:
            return APIExperiment(self._api, self.workspace, self.project, item)
        except Exception:  # regular expression, perhaps
            return [
                APIExperiment(self._api, self.workspace, self.project, exp.key)
                for exp in self
                if re.match(item, exp.key)
                or (exp.name is not None and re.match(item, exp.name))
            ]

    def __repr__(self):
        return str([experiment for experiment in self])

    def __len__(self):
        return len(
            [
                1
                for x in self._api._get(self.workspace, self.project, include=True)
                if self._api._get(self.workspace, self.project, x)["is_key"]
            ]
        )

    def __iter__(self):
        return iter(
            [
                APIExperiment(self._api, self.workspace, self.project, x)
                for x in self._api._get(self.workspace, self.project, include=True)
                if self._api._get(self.workspace, self.project, x)["is_key"]
            ]
        )


class Projects(object):
    def __init__(self, api, workspace):
        """
        The REST API object for accessing the projects.
        """
        self._api = api
        self.workspace = workspace
        self._api._build_cache(workspace)

    @property
    def data(self):
        """
        Return info on workspace.
        """
        return {
            "workspace": self.workspace,
            "projects": list(self._api._get(self.workspace, include=True).keys()),
        }

    def __getitem__(self, item):
        if isinstance(item, int):
            return APIExperiments(self._api, self.workspace, list(self)[item])
        return APIExperiments(self._api, self.workspace, item)

    def __repr__(self):
        return str([key for key in self])

    def __len__(self):
        return len(self._api._get(self.workspace, include=True).keys())

    def __iter__(self):
        return (key for key in self._api._get(self.workspace, include=True).keys())


class Workspaces(object):
    def __init__(self, api):
        """
        The REST API object for accessing the workspaces.
        """
        self._api = api

    def __getitem__(self, item):
        if isinstance(item, int):
            return Projects(self._api, list(self)[item])
        if "/" in item:
            workspace, project = item.split("/", 1)
            if "/" in project:
                project, exp = project.split("/", 1)
                return self[workspace][project][exp]
            else:
                return self[workspace][project]
        else:
            return Projects(self._api, item)

    def __repr__(self):
        return str([key for key in self])

    def __len__(self):
        return len(
            [x for x in self._api._get().keys() if self._api._get(x)["is_owner"]]
        )

    def __iter__(self):
        return iter(
            [x for x in self._api._get().keys() if self._api._get(x)["is_owner"]]
        )


class API(object):
    """
    The API class is used as a Python interface to the Comet.ml REST
    API.

    You can use an instance of the API() class to quickly and easily
    access all of your logged information at [comet.ml](https://comet.ml),
    including metrics, parameters, images, tags, and assest.

    ```
    >>> import comet_ml
    >>>> comet_api = comet_ml.API()

    ## Return all of my workspace names in a list:
    >>> comet_api.get()

    ## Get an APIExperiment:
    >>>  experiment = comet_api.get("cometpublic/comet-notebooks/example 001")

    ## Get metrics:
    >>> experiment.metrics_raw["train_accuracy"]

    ## Get the `ExistingExperiment`:
    >>> existing_exp = comet_ml.ExistingExperiment(experiment.key)
    ```

    Note that the data received from API.get() is cached. To reset
    the cache, get create a new API() instance.

    The API instance also gives you access to the low-level REST API function
    calls:

    ```
    >>> comet_api.get_experiment_parameters(experiment_key)
    ```

    will return the JSON data from the REST API:

    ```
    [{'name': 'batch_size',
      'valueMax': '100',
      'valueMin': '100',
      'valueCurrent': '100',
      'timestampMax': 1539798169687,
      'timestampMin': 1539798169687,
      'timestampCurrent': 1539798169687},
     ...]
    ```

    Note that the low-level methods return uncached data.

    For more information on the low-level interface,
    see [REST API](../../rest-api/getting-started/).

    For more usage examples, see [Comet REST examples](../Comet-REST-API/).

    """

    DEFAULT_VERSION = "v1"
    URLS = {"v1": {"SERVER": _get_server_url(), "REST": "/api/rest/v1/"}}
    COMET_HEADER = "Authorization"

    def __init__(self, api_key=None, rest_api_key=None, version=None, persistent=True):
        """
        Application Programming Interface to the Comet REST interface.

        Args:
            api_key: Optional. Your private COMET_API_KEY (or store in
                .env)
            rest_api_key: Optional. Your private COMET_REST_API_KEY
                (or store in .env)
            version: Optional. The version of the REST API to use.
            persistent: Default True. Use a persistent connection?

        Example:
        ```
        >>> from comet_ml import API
        >>> comet_api = API()
        >>> comet_api.get()
        ['project1', 'project2', ...]
        ```
        """
        self._session = None if not persistent else get_backend_session()
        self._version = version if version is not None else self.DEFAULT_VERSION
        self._config = get_config()
        self._rest_api_key = get_rest_api_key(rest_api_key, self._config)
        self._api_key = get_api_key(api_key, self._config)
        self.update_cache()

    def update_cache(self):
        """
        Refresh the cache from live server data.
        """
        self._rebuild_cache()
        self.workspaces = Workspaces(self)

    def _rebuild_cache(self):
        self._CACHE = {
            w: {"projects": {}, "is_owner": True} for w in self.get_workspaces()
        }

    def get(self, workspace=None, project=None, experiment=None):
        """
        Get the following items:
            * list of workspace names, given no arguments
            * list of project names, given a workspace name
            * list of experiment names/keys, given workspace and project names
            * an experiment, given workspace, project, and experiemnt name/key

        `workspace`, `project`, and `experiment` can also be given as a single
        string, delimited with a slash.

        Note that `experiment` can also be a regular expression.
        """
        ## First, we check for delimiters:
        if workspace is not None and "/" in workspace:
            if project is not None:
                raise SyntaxError(
                    "Can't use slash format in workspace name "
                    + "and provide project name"
                )
            workspace, project = workspace.split("/", 1)
        if project is not None and "/" in project:
            if experiment is not None:
                raise SyntaxError(
                    "Can't use slash format in project name "
                    + "and provide experiment key/name"
                )
            project, experiment = project.split("/", 1)
        ## Now, return the appropriate item:
        if workspace is None:
            return self.workspaces
        elif project is None:
            return self.workspaces[workspace]
        elif experiment is None:
            return self.workspaces[workspace][project]
        else:
            return self.workspaces[workspace][project][experiment]

    def _get(self, workspace=None, project=None, experiment_key=None, include=False):
        if workspace is None:
            return self._CACHE
        elif project is None:
            if include:
                return self._CACHE[workspace]["projects"]
            else:
                return self._CACHE[workspace]
        elif experiment_key is None:
            if include:
                return self._CACHE[workspace]["projects"][project]["experiments"]
            else:
                return self._CACHE[workspace]["projects"][project]
        else:
            return self._CACHE[workspace]["projects"][project]["experiments"][
                experiment_key
            ]

    def _set(self, workspace, project, experiment_key, data):
        self._CACHE[workspace]["projects"][project]["experiments"][
            experiment_key
        ] = data

    def _build_cache(self, workspace, project=None, experiment_name=None):
        if workspace not in self._CACHE:
            self._CACHE[workspace] = {"projects": {}, "is_owner": False}
        if self._CACHE[workspace]["projects"] == {}:
            self._CACHE[workspace]["projects"] = {
                w["project_name"]: w for w in self.get_projects(workspace)
            }
        if project is not None:
            if project not in self._CACHE[workspace]["projects"]:
                self._CACHE[workspace]["projects"][project] = {}
                self._CACHE[workspace]["projects"][project]["project_id"] = project
            if "experiments" not in self._CACHE[workspace]["projects"][project]:
                self._CACHE[workspace]["projects"][project]["experiments"] = {}
                project_id = self._CACHE[workspace]["projects"][project]["project_id"]
                for d in self.get_experiment_data(project_id):
                    d["is_key"] = True
                    self._CACHE[workspace]["projects"][project]["experiments"][
                        d["experiment_key"]
                    ] = d
        if project is not None and project not in self._CACHE[workspace]["projects"]:
            raise Exception(
                "no such project '%s' for workspace '%s'" % (project, workspace)
            )
        if experiment_name is not None:
            if (
                experiment_name
                not in self._CACHE[workspace]["projects"][project]["experiments"]
            ):
                ## FIXME: replace with new endpoint
                ## need to go through all the experiments in this project
                retval = None
                for experiment_key in list(
                    self._CACHE[workspace]["projects"][project]["experiments"]
                ):
                    data = self._CACHE[workspace]["projects"][project]["experiments"][
                        experiment_key
                    ]
                    if "_other" not in data:
                        data["_other"] = self.get_experiment_other(experiment_key)
                    data["other"] = [x["name"] for x in data["_other"]]
                    names = [
                        x["valueCurrent"] for x in data["_other"] if x["name"] == "Name"
                    ]
                    if len(names) > 0:
                        data["_name"] = names[0]
                        new_data = copy.deepcopy(data)
                        new_data["is_key"] = False
                        self._CACHE[workspace]["projects"][project]["experiments"][
                            names[0]
                        ] = new_data
                        if data["_name"] == experiment_name:
                            retval = experiment_key
                if retval is None:
                    raise Exception("no such experiment name: '%s'" % experiment_name)

    def get_url(self, version=None):
        """
        Returns the URL for this version of the API.
        """
        version = version if version is not None else self._version
        return self.URLS[version]["SERVER"] + self.URLS[version]["REST"]

    def get_url_server(self, version=None):
        """
        Returns the URL server for this version of the API.
        """
        version = version if version is not None else self._version
        return self.URLS[version]["SERVER"]

    def get_url_end_point(self, end_point, version=None):
        """
        Return the URL + end point.
        """
        return self.get_url(version) + end_point

    def get_request(self, end_point, params, return_type="json"):
        """
        Given an end point and a dictionary of params,
        return the results.
        """
        from . import __version__

        url = self.get_url_end_point(end_point)
        LOGGER.debug("API.get_request: url = %s, params = %s", url, params)
        headers = {
            self.COMET_HEADER: self._rest_api_key,
            "PYTHON-SDK-VERSION": __version__,
        }
        if self._session is not None:
            response = self._session.get(url, params=params, headers=headers)
        else:
            response = requests.get(url, params=params, headers=headers)
        raise_exception = None
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code == 401:
                raise_exception = ValueError("Invalid COMET_REST_API_KEY")
            else:
                raise
        if raise_exception:
            raise raise_exception
        # Return data based on return_type:
        if return_type == "json":
            return response.json()
        elif return_type == "binary":
            return response.content
        elif return_type == "text":
            return response.text

    def post_request(self, end_point, json=None, **kwargs):
        """
        Given an end point and a dictionary of json,
        post the json, and return the results.
        """
        from . import __version__

        url = self.get_url_end_point(end_point)
        if json is None:
            json = {}
        LOGGER.debug("API.post_request: url = %s, json = %s", url, json)
        headers = {
            self.COMET_HEADER: self._rest_api_key,
            "PYTHON-SDK-VERSION": __version__,
            "Content-Type": "application/json",
        }
        if "files" in kwargs:
            del headers["Content-Type"]
        if self._session is not None:
            response = self._session.post(url, headers=headers, json=json, **kwargs)
        else:
            response = requests.post(url, headers=headers, json=json, **kwargs)
        raise_exception = None
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            if exception.response.status_code == 401:
                raise_exception = ValueError("Invalid COMET_REST_API_KEY")
            else:
                raise
        if raise_exception:
            raise raise_exception
        return response.json()

    def get_version(self):
        """
        Return the default version of the API.
        """
        return self._version

    def get_workspaces(self):
        """
        Return the names of the workspaces for this user.
        """
        params = {}
        results = self.get_request("workspaces", params)
        return results["workspaces"]

    def get_projects(self, workspace):
        """
        Return the ids of the projects in a workspace.
        """
        params = {"workspace": workspace}
        results = self.get_request("projects", params)
        return results["projects"]

    def get_experiment_keys(self, project_id):
        """
        Get the experiment_keys given a project id.
        """
        params = {"projectId": project_id}
        results = self.get_request("experiments", params)
        return [exp["experiment_key"] for exp in results["experiments"]]

    def get_experiment_data(self, project_id):
        """
        Returns the JSON data for all experiments
        in a project.
        """
        params = {"projectId": project_id}
        results = self.get_request("experiments", params)
        return results["experiments"]

    def get_experiment_html(self, experiment_key):
        """
        Returns the HTML data given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/html", params)
        return results["html"]

    def get_experiment_code(self, experiment_key):
        """
        Returns the code associated with an experiment (or None
        if there isn't any code), given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/code", params)
        return results["code"]

    def get_experiment_stdout(self, experiment_key):
        """
        Returns the standard output of an experiment,
        given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/stdout", params)
        return results["output"]

    def get_experiment_installed_packages(self, experiment_key):
        """
        Return the list of installed Python packages at the
        time an experiment was run.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/installed-packages", params)
        return results["packages"]

    def get_experiment_os_packages(self, experiment_key):
        """
        Return the list of installed OS packages at the
        time an experiment was run.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/os-packages", params)
        return results["packages"]

    def get_experiment_graph(self, experiment_key):
        """
        Return the model graph, given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/graph", params)
        return results["graph"]

    def get_experiment_images(self, experiment_key):
        """
        Return the experiment images, given an experiment
        key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/images", params)
        return results["images"]

    def get_experiment_parameters(self, experiment_key, param=None):
        """
        Return the experiment parameters, given an experiment key.
        Optionally, also if you provide the parameter name, the
        function will only return the value(s) of the
        parameter.

        Examples:
        ```
        >>> from comet_ml import API
        >>> comet_api = API()
        >>> comet_api.get("myworkspace/project1").parameters[0]["valueCurrent"]
        0.1
        >>> [[(exp, "hidden_size", int(param["valueCurrent"]))
        ...   for param in exp.parameters
        ...   if param["name"] == "hidden_size"][0]
        ...  for exp in comet_api.get("dsblank/pytorch/.*")]
        [(<APIExperiment>, 'hidden_size', 128),
         (<APIExperiment>, 'hidden_size', 64)]
        >>> comet_api.get("myworkspace/myproject").parameters
        [{"name": "learning_rate", ...}, {"name": "hidden_layer_size", ...}]
        ```
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/params", params)
        if param is not None:
            retval = [
                p["valueCurrent"] for p in results["results"] if p["name"] == param
            ]
            return retval
        else:
            return results["results"]

    def get_experiment_metrics(self, experiment_key, metric=None):
        """
        Return the experiment metrics, given an experiment key.
        Optionally, also if you provide the metric name, the
        function will only return the value(s) of the
        metric.

        Examples:
        ```
            >>> from comet_ml import API
            >>> comet_api = API()
            >>> comet_api.get_experiment_metrics("accuracy")
            [0.0, 0.1, 0.5, ...]
            >>> comet_api.get_experiment_metrics("loss")
            [1.3, 1.2, 0.9, 0.6, ...]
            >>> comet_api.get_experiment_metrics()
            [{"name": "accuracy", ...}, {"name": "loss", ...}]
        ```
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/metrics", params)
        if metric is not None:
            retval = [
                m["valueCurrent"] for m in results["results"] if m["name"] == metric
            ]
            return retval
        else:
            return results["results"]

    def get_experiment_other(self, experiment_key, other=None, value=None):
        """
        Get the other items logged, given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/log-other", params)
        if other is not None:
            if value is not None:
                retval = [
                    m
                    for m in results["logOtherList"]
                    if m["name"] == other and m["valueCurrent"] == value
                ]
            else:
                retval = [
                    m["valueCurrent"]
                    for m in results["logOtherList"]
                    if m["name"] == other
                ]
            return retval
        else:
            return results["logOtherList"]

    def get_experiment_metrics_raw(self, experiment_key, metric=None):
        """
        Get the other items logged (in raw form), given an experiment key.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/metrics-raw", params)
        if metric is not None:
            retval = [
                m["valueCurrent"] for m in results["metrics"] if m["name"] == metric
            ]
            return retval
        else:
            return results["metrics"]

    def get_experiment_asset_list(self, experiment_key):
        """
        Get a list of assets associated with experiment.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("asset/get-asset-list", params)
        return results

    def get_experiment_asset(self, experiment_key, asset_id, return_type="binary"):
        """
        Get an asset, given the experiment_key and asset_id.

        Arguments:
            experiment_key: the experiment ID
            asset_id: the asset ID
            return_type: the type of object returned. Default is
                "binary". Options: "binary" or "text"
        """
        params = {"experimentKey": experiment_key, "assetId": asset_id}
        results = self.get_request("asset/get-asset", params, return_type=return_type)
        return results

    def get_experiment_system_details(self, experiment_key):
        """
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/system-details", params)
        return results

    def get_experiment_git_patch(self, experiment_key):
        """
        Get the git-patch associated with this experiment.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("git/get-patch", params)
        return results

    def get_experiment_git_metadata(self, experiment_key):
        """
        Get the git-metadata associated with this experiment.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/git-metadata", params)
        return results

    def get_experiment_tags(self, experiment_key):
        """
        Get the git-metadata associated with this experiment.
        """
        params = {"experimentKey": experiment_key}
        results = self.get_request("experiment/tags", params)
        return results["tags"]

    ## ---------------------------------------------------------

    def set_experiment_other(self, experiment_key, key, value):
        """
        Set an other key/value pair for an experiment.
        """
        json = {"experimentKey": experiment_key, "key": key, "val": value}
        results = self.post_request("write/log-other", json)
        self._rebuild_cache()
        return results

    def set_experiment_parameter(self, experiment_key, parameter, value, step=None):
        """
        Set a parameter name/value pair for an experiment.
        """
        json = {
            "experimentKey": experiment_key,
            "paramName": parameter,
            "paramValue": value,
        }
        if step is not None:
            json["step"] = step
        results = self.post_request("write/parameter", json)
        self._rebuild_cache()
        return results

    def set_experiment_metric(self, experiment_key, metric, value, step=None):
        """
        Set a metric name/value pair for an experiment.
        """
        json = {
            "experimentKey": experiment_key,
            "metricName": metric,
            "metricValue": value,
        }
        if step is not None:
            json["step"] = step
        results = self.post_request("write/metric", json)
        self._rebuild_cache()
        return results

    def set_experiment_start_end(self, experiment_key, start, end):
        """
        Set an experiment start/end time in miliseconds.
        """
        json = {
            "experimentKey": experiment_key,
            "start_time_millis": start,
            "end_time_millis": end,
        }
        results = self.post_request("write/experiment-start-end-time", json)
        self._rebuild_cache()
        return results

    def set_experiment_html(self, experiment_key, html, overwrite=False):
        """
        Set, or append onto, an experiment's HTML.
        """
        json = {"experimentKey": experiment_key, "html": html, "override": overwrite}
        results = self.post_request("write/html", json)
        self._rebuild_cache()
        return results

    def upload_asset(
        self, experiment_key, filename, step=None, overwrite=None, context=None
    ):
        """
        Upload an asset to an experiment.
        """
        params = {"experimentKey": experiment_key}
        json = {}
        files = {"file": (filename, open(filename, "rb"))}
        if step is not None:
            json["step"] = step
        if overwrite is not None:
            json["overwrite"] = overwrite
        if context is not None:
            json["context"] = context
        results = self.post_request(
            "write/upload-asset", json, params=params, files=files
        )
        return results

    def upload_image(
        self,
        experiment_key,
        filename,
        image_name=None,
        step=None,
        overwrite=None,
        context=None,
    ):
        """
        Upload an image asset to an experiment.
        """
        params = {"experimentKey": experiment_key}
        if image_name is not None:
            params["figureName"] = image_name
        if step is not None:
            params["step"] = step
        if overwrite is not None:
            params["overwrite"] = overwrite
        if context is not None:
            params["context"] = context
        files = {"file": (filename, open(filename, "rb"))}
        results = self.post_request("write/upload-image", params=params, files=files)
        return results

    def create_experiment(self, workspace, project=None, experiment_name=None):
        """
        Create an experiment and return its associated APIExperiment.
        """
        if "/" in workspace:
            if project is not None:
                raise ValueError("cannot name project with delimited workspace name")
            workspace, project = workspace.split("/", 1)
        if "/" in project:
            if experiment_name is not None:
                raise ValueError("cannot name experiment with delimited project name")
            project, experiment_name = project.split("/", 1)
        json = {"workspace": workspace, "project_name": project}
        if experiment_name is not None:
            json["experiment_name"] = experiment_name
        results = self.post_request("write/new-experiment", json)
        ## Add experiment_key, experiment_name to cache:
        self._rebuild_cache()
        exp = self.get(workspace, project, results["experimentKey"])
        exp.other
        return exp

    def create_symlink(self, workspace, project, experiment_name=None):
        """
        Create a copy of an experiment in this workspace/project.
        """
        json = {"workspace": workspace, "project_name": project}
        if experiment_name is not None:
            json["experiment_name"] = experiment_name
        results = self.post_request("write/symlink", json)
        self._rebuild_cache()
        return results

    def delete_experiment(self, experiment_keys):
        """
        Delete one or more experiments.
        """
        if isinstance(experiment_keys, six.string_types):
            params = {"experimentKey": experiment_keys, "hardDelete": True}
            results = self.get_request("write/delete-experiment", params)
        else:  # assume it is a list/array/tuple etc:
            results = []
            for experiment_key in experiment_keys:
                result = self.delete_experiment(experiment_key)
                results.append(result)
        return results

    def archive_experiment(self, experiment_keys):
        """
        Archive one or more experiments.
        """
        if isinstance(experiment_keys, six.string_types):
            params = {"experimentKey": experiment_keys, "hardDelete": False}
            results = self.get_request("write/delete-experiment", params)
        else:  # (tuple, list, etc):
            results = []
            for experiment_key in experiment_keys:
                result = self.archive_experiment(experiment_key)
                results.append(result)
        return results
