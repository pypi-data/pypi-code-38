"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import dill
from pathlib import Path
import os

from .run import Run, RemoteRun
from .properties import PropertyManager
from contextlib import closing
from datetime import datetime
from jinja2 import Template
import maya
from .camel import CamelResource
from typing import Dict, List
import deprecation
from cortex_client import ExperimentClient
from requests.exceptions import HTTPError
from .exceptions import APIException


def _to_html(exp):
    runs = exp.runs()

    template = """
                    <style>
                        #table1 {
                          border: solid thin;
                          border-collapse: collapse;
                        }
                        #table1 caption {
                          padding-bottom: 0.5em;
                        }
                        #table1 th,
                        #table1 td {
                          border: solid thin;
                          padding: 0.5rem 2rem;
                        }
                        #table1 td {
                          white-space: nowrap;
                        }
                        #table1 td {
                          border-style: none solid;
                          vertical-align: top;
                        }
                        #table1 th {
                          padding: 0.2em;
                          vertical-align: middle;
                          text-align: center;
                        }
                        #table1 tbody td:first-child::after {
                          content: leader(". "); '
                        }
                    </style>
                    <table id="table1">
                        <caption><b>Experiment:</b> {{name}}</caption>
                        <thead>
                        <tr>
                            <th rowspan="2">ID</th>
                            <th rowspan="2">Date</th>
                            <th rowspan="2">Took</th>
                            <th colspan="{{num_params}}" scope="colgroup">Params</th>
                            <th colspan="{{num_metrics}}" scope="colgroup">Metrics</th>
                        </tr>
                        <tr>
                            {% for param in param_names %}
                            <th>{{param}}</th>
                            {% endfor %}
                            {% for metric in metric_names %}
                            <th>{{metric}}</th>
                            {% endfor %}
                        </tr>
                        </thead>
                        <tbody>
                            {% for run in runs %}
                            <tr>
                            <td>{{run.id}}</td>
                            <td>{{maya(run.start_time)}}</td>
                            <td>{{'%.2f' % run.took}} s</td>
                            {% for param in param_names %}
                            <td>{{run.params.get(param, "&#x2011;")}}</td>
                            {% endfor %}
                            {% for metric in metric_names %}
                            <td>{{'%.6f' % run.metrics.get(metric, 0.0)}}</td>
                            {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>"""

    num_params = 0
    num_metrics = 0
    param_names = set()
    metric_names = set()
    if len(runs) > 0:
        for one_run in runs:
            param_names.update(one_run.params.keys())
            num_params = len(param_names)
            metric_names.update(one_run.metrics.keys())
            num_metrics = len(metric_names)

    t = Template(template)
    return t.render(
            name=exp.name, 
            runs=runs, 
            maya=maya.MayaDT, 
            num_params=num_params, 
            param_names=sorted(list(param_names)), 
            num_metrics=num_metrics, 
            metric_names=sorted(list(metric_names))
            )


class Experiment(CamelResource):
    """
    Tracks runs, associated parameters, metrics, and artifacts of experiments.
    """

    def __init__(self, document: Dict, client: ExperimentClient):
        super().__init__(document, False)
        self._client = client
        if not self.meta:
            self.meta = {}

    @staticmethod
    def get_experiment(name, client: ExperimentClient, **kwargs):
        """
        Fetches or creates an experiment to work with.

        :param name: The name of the experiment to retrieve.
        :param client: The client instance to use.
        :return: An experiment object.
        """
        try:
            exp = client.get_experiment(name)
        except HTTPError:
            # Likely a 404, try to create a new experiment
            exp = client.save_experiment(name, **kwargs)

        return Experiment(exp, client)

    def start_run(self) -> Run:
        return RemoteRun.create(self, self._client)

    def save_run(self, run: Run):
        self._client.update_run(self.name, run.id, took=run.took, startTime=run.start_time, endTime=run.end_time)

    def reset(self, filter=None, sort=None, limit=None):
        self._client.delete_runs(self.name, filter, sort, limit)

    def set_meta(self, prop, value):
        self.meta[prop] = value
        self._client.save_experiment(self.name, **self.to_camel())

    def runs(self) -> List[Run]:
        runs = self._client.list_runs(self.name)
        return [RemoteRun.from_json(r, self) for r in runs]

    def get_run(self, run_id) -> Run:
        run = self._client.get_run(self.name, run_id)
        return RemoteRun.from_json(run, self)

    def last_run(self) -> Run:
        sort = {'endTime': -1}
        runs = self._client.find_runs(self.name, {}, sort=sort, limit=1)
        if len(runs) == 1:
            return RemoteRun.from_json(runs[0], self)
        raise APIException('Last run for experiment {} not found'.format(self.name))

    def find_runs(self, filter, sort, limit: int) -> List[Run]:
        runs = self._client.find_runs(self.name, filter or {}, sort=sort, limit=limit)
        return [RemoteRun.from_json(r, self) for r in runs]

    def load_artifact(self, run: Run, name: str):
        return dill.loads(self._client.get_artifact(self.name, run.id, name))

    def to_camel(self, camel='1.0.0'):
        return {
            'camel': camel,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'tags': self.tags or [],
            'meta': self.meta or {}
        }

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        from IPython.display import (display, HTML)
        display(HTML(self._repr_html_()))


class LocalExperiment:
    """
    Runs experiment locally, not using Cortex services.
    """
    config_file = 'config.yml'
    root_key = 'experiment'
    dir_cortex = '.cortex'
    dir_local = 'local'
    dir_artifacts = 'artifacts'
    dir_experiments = 'experiments'
    runs_key = 'runs'

    def __init__(self, name):
        self._name = name

        self._work_dir = Path.home() / self.dir_cortex / self.dir_local / self.dir_experiments / self.name
        self._work_dir.mkdir(parents=True, exist_ok=True)
        Path(self._work_dir / self.dir_artifacts).mkdir(parents=True, exist_ok=True)

        # Initialize config
        pm = PropertyManager()
        try:
            pm.load(str(self._work_dir / self.config_file))
        except FileNotFoundError:
            pm.set('meta', {'created': str(datetime.now())})

        self._config = pm

    @property
    def name(self):
        """
        Name of the experiment.
        """
        return self._name

    def start_run(self) -> Run:
        """
        Creates a run for the experiment.
        """
        return Run(self)

    def save_run(self, run: Run):
        """
        Saves a run.

        :param run: The run you want to save.
        """
        updated_runs = []
        runs = self._config.get(self._config.join(self.root_key, self.runs_key)) or []
        replaced = False
        if len(runs) > 0:
            for r in runs:
                if r['id'] == run.id:
                    updated_runs.append(run.to_json())
                    replaced = True
                else:
                    updated_runs.append(r)

        if not replaced:
            updated_runs.append(run.to_json())

        self._config.set(self._config.join(self.root_key, self.runs_key), updated_runs)
        self._save_config()

        for name, artifact in run.artifacts.items():
            with closing(open(self.get_artifact_path(run, name), 'wb')) as f:
                dill.dump(artifact, f)

    def reset(self):
        """
        Resets the experiement, removing all associated configuration and runs.
        """
        self._config.remove_all()
        self.clean_dir(self._work_dir)
        self.clean_dir(Path(self._work_dir / self.dir_artifacts))

    def clean_dir(self, dir_to_clean):
        """
        Removes only the files from the given directory
        """
        for f in os.listdir(dir_to_clean):
             if os.path.isfile(os.path.join(dir_to_clean, f)):
                 os.remove(os.path.join(dir_to_clean, f))

    @deprecation.deprecated(deprecated_in='5.5.0', removed_in='6.0.0', details='No replacement')
    def set_pipeline(self, pipeline):
        """
        Attaches a pipeline to the experiment.

        :param pipeline: Pipeline to attach to the experiment.
        """
        self._config.set('pipeline', {'dataset': pipeline._ds.name, 'name': pipeline.name})
        self._save_config()

    def set_meta(self, prop, value):
        """
        Associates metadata properties with the experiment.

        :param prop: The name of the metadata property to associate with the experiment.
        :param value: The value of the metadata property to associate with the experiment.
        """
        meta = self._config.get('meta')
        meta[prop] = value
        self._config.set('meta', meta)
        self._save_config()

    def runs(self) -> List[Run]:
        """
        Returns the runs associated with the experiment.
        """
        props = self._config
        runs = props.get(props.join(self.root_key, self.runs_key)) or []
        return [Run.from_json(r, self) for r in runs]

    def get_run(self, run_id: str) -> Run:
        """
        Gets a particular run from the runs in this experiment.
        """
        for r in self.runs():
            if r.id == run_id:
                return r
        return None

    def last_run(self) -> Run:
        runs = self.runs()
        if len(runs) > 0:
            return runs[-1]
        return None

    def find_runs(self, filter, sort, limit: int) -> List[Run]:
        raise NotImplementedError('find_runs is not supported in local mode')

    def _save_config(self):
        self._config.save(self._work_dir / self.config_file)

    def load_artifact(self, run: Run, name: str, extension: str = 'pk'):
        """
        Returns a particualr artifact created by the given run of the experiement.

        :param run: The run that generated the artifact requested.
        :param name: The name of the artifact.
        :param extension: An optional extension (defaults to 'pk').
        """
        artifact_file = self.get_artifact_path(run, name, extension)
        with closing(open(artifact_file, 'rb')) as f:
            return dill.load(f)

    def get_artifact_path(self, run: Run, name: str, extension: str = 'pk'):
        """
        Returns the fully qualified path to a particular artifact.

        :param run: The run that generated the artifact requested.
        :param name: The name of the artifact.
        :param extension: An optional extension (defaults to 'pk').
        """
        return self._work_dir / self.dir_artifacts / "{}_{}.{}".format(name, run.id, extension)

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        """
        Provides html output of the experiment.
        """
        from IPython.display import (display, HTML)
        display(HTML(self._repr_html_()))
