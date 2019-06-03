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

import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from cortex_client import DatasetsClient
from .logger import getLogger
from .camel import CamelResource
from .utils import log_message
from .pipeline import Pipeline
from .pipeline_loader import PipelineLoader
from .properties import PropertyManager
from abc import ABC, abstractmethod

log = getLogger(__name__)

class _Viz:

    """
    A wrapper that assists users in running multiple commonly used visualizations on the same dataframe; not meant to be directly instantiated by clients.
    """

    def __init__(self, df, figsize=(18, 9)):
        self.df = df
        self.corr_m = df.corr()

        if figsize is None or not isinstance(figsize, tuple):
            self.figsize = (18, 9)
        else:
            self.figsize = figsize

    def show_corr(self, column: str):
        cm_sorted = self.corr_m[column].sort_values(ascending=False)
        plt.rcParams['figure.figsize'] = self.figsize
        plt.xticks(rotation=90)
        sns.barplot(x=cm_sorted.index, y=cm_sorted)
        plt.show()
        plt.clf()

    def show_corr_heatmap(self, **kwargs):
        plt.rcParams['figure.figsize'] = self.figsize
        sns.heatmap(self.corr_m, annot=True, cmap=kwargs.get('cmap', 'BuGn'), robust=True, fmt=kwargs.get('fmt', '.1f'))
        plt.show()
        plt.clf()

    def show_dist(self, column: str):
        try:
            from scipy.stats import norm
            fit = norm
        except ImportError:
            fit = None

        plt.rcParams['figure.figsize'] = self.figsize
        sns.distplot(self.df[column], fit=fit)
        plt.show()
        plt.clf()

    def show_probplot(self, column: str):
        try:
            from scipy import stats
            plt.rcParams['figure.figsize'] = self.figsize
            stats.probplot(self.df[column], plot=plt)
            plt.show()
            plt.clf()
        except ImportError:
            raise Exception('show_probplot requires SciPy to be installed')

    def show_corr_pairs(self, column: str, threshold=0.7):
        cm = self.df.corr()
        values = list(cm[column].values)
        keys = list(cm[column].keys())
        vars = [i for i in keys if values[keys.index(i)] > threshold]

        plt.rcParams['figure.figsize'] = self.figsize
        sns.pairplot(self.df, height=3, vars=vars)
        plt.show()
        plt.clf()


class _DatasetPipelineLoader(PipelineLoader):

    def __init__(self, ds):
        super().__init__()
        self.ds = ds

    def add_pipeline(self, name, pipeline):
        super().add_pipeline(name, pipeline)
        self.ds._add_pipeline(name, pipeline)

    def get_pipeline(self, name):
        try:
            p = self.ds._client.get_pipeline(self.ds.name, name)
            pipeline = Pipeline.load(p, self)
            self.add_pipeline(name, pipeline)
            return pipeline
        except:
            return super().get_pipeline(name)

    def remove_pipeline(self, name):
        super().remove_pipeline(name)
        self.ds._remove_pipeline(name)


class AbstractDataset(ABC):
    """
    Abstract base class for datasets.
    """
    @abstractmethod
    def get_dataframe(self):
        raise NotImplementedError()

    @abstractmethod
    def get_stream(self):
        raise NotImplementedError()

    @abstractmethod
    def as_pandas(self):
        raise NotImplementedError()

    def visuals(self, df=None, figsize=(18, 9)):
        if df is None:
            df = self.as_pandas()
        return _Viz(df, figsize)

    @abstractmethod
    def save(self):
        raise NotImplementedError()

    @abstractmethod
    def to_camel(self):
        raise NotImplementedError()

    @abstractmethod
    def pipeline(self, name, clear_cache=False, depends=None):
        raise NotImplementedError()


class Dataset(AbstractDataset, CamelResource):

    """
    Defines the data and query parameters for accessing inputs to
    a managed content file or database connection.
    """

    def __init__(self, ds, client: DatasetsClient):
        super().__init__(ds, read_only=False)
        self._client = client
        self._work_dir = Path.cwd() / 'datasets' / self.name
        self._pipeline_loader = _DatasetPipelineLoader(self)

        # Cache all configured pipelines into our Pipeline loader
        if self.pipelines:
            for name in self.pipelines.keys():
                self._pipeline_loader.get_pipeline(name)
        else:
            self.pipelines = {}

    @staticmethod
    def get_dataset(name, client: DatasetsClient):
        """
        Gets a dataset.

        :param name: The name of the dataset to retrieve.
        :param client: The client instance to use.
        :return: A dataset object.
        """
        uri = '/'.join(['datasets', name])
        log.debug('Getting dataset using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri)
        r.raise_for_status()

        return Dataset(r.json(), client)

    def get_dataframe(self):
        """
        Gets the dataframe for the dataset.
        """
        return self._client.get_dataframe('{}:{}'.format(self.name, self.version))

    def get_stream(self):
        """
        Streams the data coming from the dataset.
        """
        return self._client.get_stream('{}:{}'.format(self.name, self.version))

    def as_pandas(self):
        """
        Gets a pandas dataframe for the dataset.
        """
        df = self.get_dataframe()
        columns = df.get('columns')
        values = df.get('values')

        try:
            import pandas as pd
            return pd.DataFrame(values, columns=columns)
        except ImportError:
            log.warn('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')
            return {'columns': columns, 'values': values}

    def visuals(self, df=None, figsize=(18, 9)):
        """
        Gets a visualization.

        :param df: Optional dataframe for the visualization.
        :param figsize: A two element tuple specifing the width and height of the visualization.
        :return: A visualization object.
        """
        if df is None:
            df = self.as_pandas()
        return _Viz(df, figsize)

    def save(self):
        from .builder.dataset_builder import DatasetBuilder
        b = DatasetBuilder(self.name, self._client, self.camel)
        return b.from_dataset(self).build()

    def to_camel(self):
        from .builder.dataset_builder import DatasetBuilder
        b = DatasetBuilder(self.name, self._client, self.camel)
        return b.from_dataset(self).to_camel()

    def _add_pipeline(self, name, pipeline):
        self.pipelines[name] = pipeline

    def _remove_pipeline(self, name):
        if name in self.pipelines:
            del self.pipelines[name]

    def pipeline(self, name, clear_cache=False, depends=None):
        """
        Gets a pipeline for the dataset.

        :param name: name of the pipeline
        :param clear_cache: a flag to indicate whether previous results for the pipeline should be cleared
        :param depends: a list of pipeline names upon which this pipeline depends
        """
        p = self._pipeline_loader.get_pipeline(name)
        if clear_cache:
            # TODO clear any caches - e.g. for local mode
            pass

        if depends is not None:
            for d in depends:
                p.add_dependency(self._pipeline_loader.get_pipeline(d))

        return p


class LocalDataset(AbstractDataset):
    """
    References datasets that are external to Cortex.
    """

    config_file = 'config.yml'
    root_key = 'dataset'
    dir_cortex = '.cortex'
    dir_local = 'local'
    dir_data = 'data'
    dir_datasets = 'datasets'
    camel = '1.0.0'
    environment_id = 'cortex/local'

    def __init__(self, name):
        self._work_dir = Path.home() / self.dir_cortex / self.dir_local / self.dir_datasets / name
        self._work_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir = Path(self._work_dir / self.dir_data)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._pipeline_loader = PipelineLoader()

        # Initialize config
        pm = PropertyManager()
        try:
            # Load local dataset configuration
            pm.load(str(self._work_dir / self.config_file))

            # Cache all configured pipelines into our Pipeline loader
            pipelines = pm.get('pipelines') or {}
            for p_name, p_doc in pipelines.items():
                Pipeline.load(p_doc, self._pipeline_loader)
        except FileNotFoundError:
            # Set initial configuration state
            pm.set('name', name)
            pm.set('camel', self.camel)
            pm.set('_environmentId', self.environment_id)
            pm.set('createdAt', str(datetime.now()))
            pm.set('_version', 0)

        self._config = pm

    @property
    def name(self):
        return self._config.get('name')

    @name.setter
    def name(self, title):
        self._config.set('name', title)

    @property
    def version(self):
        return self._config.get('_version')

    @property
    def title(self):
        return self._config.get('title')

    @title.setter
    def title(self, title):
        self._config.set('title', title)

    @property
    def description(self):
        return self._config.get('description')

    @description.setter
    def description(self, description):
        self._config.set('description', description)

    @property
    def parameters(self):
        return self._config.get('parameters') or []

    @parameters.setter
    def parameters(self, params):
        self._config.set('parameters', params)

    def save(self):
        # Save pipelines from the loader
        pipelines = self._pipeline_loader.dump(self.camel)
        for k, v in pipelines.items():
            self._config.set(self._config.join('pipelines', k), v)

        self._config.set('_version', self.version + 1)
        self._config.save(self._work_dir / self.config_file)

        return self

    def as_pandas(self):
        return self.get_dataframe()

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def content_key(self):
        return self._config.get('content_key')

    @content_key.setter
    def content_key(self, content_key: str):
        if not content_key:
            return 
        ext = content_key.split('.')[-1]
        self._config.set('content_key', content_key)
        self._config.set('content_type', ext)

    @property
    def content_type(self):
        return self._config.get('content_type')

    def get_dataframe(self):
        try:
            import pandas as pd

            data_file = str(self._data_dir / self.content_key)

            if self.content_type == 'csv':
                return pd.read_csv(data_file)
            elif self.content_type == 'json':
                return pd.read_json(data_file, orient='records', lines=True)
            else:
                with self.get_stream() as s:
                    return pickle.load(s)
        except ImportError:
            raise ImportError('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')

    def get_stream(self):
        data_file = str(self._data_dir / self.content_key)
        return open(data_file, 'rb')

    def to_camel(self):
        pipelines = self._config.get('pipelines') or {}
        ds = {
            'camel': self.camel,
            'name': self.name,
            '_version': self.version,
            'title': self.title,
            'description': self.description,
            'parameters': self.parameters,
            'pipelines':  pipelines
        }

        return ds

    def pipeline(self, name, clear_cache=False, depends=None):
        pipelines = self._config.get('pipelines') or {}
        p_doc = pipelines.get(name)
        if p_doc:
            return Pipeline.load(p_doc, self._pipeline_loader)

        p = Pipeline(name, depends, self._pipeline_loader)
        # pipelines[name] = p.to_camel(self.camel)
        # self._config.set('pipelines', pipelines)
        self.save()

        return p
