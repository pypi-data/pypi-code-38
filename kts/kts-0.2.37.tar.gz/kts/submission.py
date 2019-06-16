from . import config
from .utils import captcha
from .feature.helper import helper_list
import os


class Submission:
    def __init__(self, exp):
        self.exp = exp
        self.fs = exp.featureset
        self.model = exp.model
        self.metric = exp.metric
        self.splitter = exp.splitter
        self.features = exp.features
        self.helpers = exp.helpers
        self.path = config.root_dir + f'submissions/{exp.identifier}/'

    def feature_source(self):
        FEATURE_SOURCE_TEMPLATE = f"""\
import kts
from kts import *


"""
        return FEATURE_SOURCE_TEMPLATE + '\n\n'.join(['@register\n' + f.source for f in self.features])

    def helper_source(self):
        HELPER_SOURCE_TEMPLATE = f"""\
import kts
from kts import *


"""
        return HELPER_SOURCE_TEMPLATE + '\n\n'.join(['@helper\n' + f.source for f in self.helpers])

    def main_source(self):
        MAIN_SOURCE_TEMPLATE = f"""
import kts
from kts import *

from features import *
from helpers import *

from {self.splitter.__module__} import {self.splitter.__class__.__name__}
{f"from {self.metric.__module__} import {self.metric.__name__}" if self.metric.__module__ != '__main__' else ""}
from {self.model.__module__} import {self.model.__class__.__name__}


splitter = {self.splitter}
metric = {self.metric.__name__}
val = Validator(splitter, metric)

{self.fs.__name__} = {self.fs.source}

{self.model.__name__} = {self.model.source}

val.score({self.model.__name__}, {self.fs.__name__})
"""
        return MAIN_SOURCE_TEMPLATE

    def write(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            os.system(f'cd {self.path} && y | kts init')
        else:
            print('Such submission already exists. Rewrite?')
            if not captcha():
                return
        with open(self.path + 'features.py', 'w') as f:
            f.write(self.feature_source())
        with open(self.path + 'helpers.py', 'w') as f:
            f.write(self.helper_source())
        with open(self.path + 'main.py', 'w') as f:
            f.write(self.main_source())
        try:
            create_submission = helper_list['create_submission']
        except:
            raise UserWarning("You should create helper with name create_submission(experiment) -> pd.DF")
        df_sub = create_submission(self.exp)
        df_sub.to_csv(self.path + 'submission.csv')


def submit(experiment):
    subm = Submission(experiment)
    subm.write()