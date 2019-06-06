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
import json
import unittest

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV, ElasticNetCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from cortex import Cortex, Message

class TestLocal(unittest.TestCase):
    """
    Test the local option using the Ames example as a model for the test.
    """

    def setUp(self):
        self.message = { 
            "properties": {}
        }

    # values for analysis test
    EXPECTED_PARAMETER_SIZE = 81
    TEST_HEATING_QC_INDEX = 40
    EXPECTED_HEATING_QC_NAME_PARAM = 'name'
    EXPECTED_HEATING_QC_NAME = 'HeatingQC'
    EXPECTED_HEATING_QC_TYPE_PARAM = 'type'
    EXPECTED_HEATING_QC_TYPE = 'string'
    TEST_DD_INDEX = 0
    EXPECTED_DD_FIRST_VALUE = '1stFlrSF'

    def test_analysis(self):
        cortex = Cortex.local()
        builder = cortex.builder()
        train_df = pd.read_csv('./test/data/ames/train.csv')
        train_ds = builder.dataset('ames-train')\
            .title('Ames Housing Training Data')\
            .from_df(train_df).build()

        self.assertEqual(len(train_ds.parameters), self.EXPECTED_PARAMETER_SIZE)
        self.assertEqual(
            train_ds.parameters[self.TEST_HEATING_QC_INDEX][self.EXPECTED_HEATING_QC_NAME_PARAM],
            self.EXPECTED_HEATING_QC_NAME
        )
        self.assertEqual(
            train_ds.parameters[self.TEST_HEATING_QC_INDEX][self.EXPECTED_HEATING_QC_TYPE_PARAM],
            self.EXPECTED_HEATING_QC_TYPE
        )

    def test_clean(self):
        cortex = Cortex.local()
        train_ds = cortex.dataset('kaggle/ames-housing-train')
        pipeline = train_ds.pipeline('clean', clear_cache=True)
        pipeline.reset()

        # adding steps to the pipeline
        def drop_unused(pipeline, df):
            df.drop(columns=['Id'], axis=1, inplace=True)
        pipeline.add_step(drop_unused)

        def drop_outliers(pipeline, df):
            df.drop(df[(df['GrLivArea'].astype(int)>4000)\
             & (df['SalePrice'].astype(int)<300000)].index, inplace=True)
        pipeline.add_step(drop_outliers)

        def fill_zero_cols(pipeline, df):
            fill_zero_cols = ['BsmtHalfBath', 'BsmtFullBath', 'BsmtFinSF2', 'GarageCars']
            [df[i].fillna(0, inplace=True) for i in fill_zero_cols]
        pipeline.add_step(fill_zero_cols)

        def fill_na_none(pipeline, df):
            df.fillna('none', inplace=True)
        pipeline.add_step(fill_na_none)

        # run it
        train_df = pd.read_csv('./test/data/ames/train.csv')
        train_df = pipeline.run(train_df)
        train_ds.save()


    def test_feature(self):
        cortex = Cortex.local()
        train_ds = cortex.dataset('kaggle/ames-housing-train')
        pipeline = train_ds.pipeline('features', depends=['clean'], clear_cache=True)
        pipeline.reset()
        def scale_target(pipeline, df):
            df['SalePrice'] = np.log1p(df['SalePrice'])

        pipeline.add_step(scale_target)

        train_df = pd.read_csv('./test/data/ames/train.csv')
        train_df = pipeline.run(train_df)
        train_ds.save()


    def test_modeling(self):
        cortex = Cortex.local()
        train_ds = cortex.dataset('kaggle/ames-housing-train')
        pipeline = train_ds.pipeline('features')
        train_df = pipeline.run(pd.read_csv('./test/data/ames/train.csv'))
        
        y = train_df['SalePrice']
        
        def drop_target(pipeline, df):
            df.drop('SalePrice', 1, inplace=True)
    
        def get_dummies(pipeline, df):
            return pd.get_dummies(df)

        pipeline = train_ds.pipeline('engineer', depends=['features'], clear_cache=True)
        pipeline.reset()
        pipeline.add_step(drop_target)
        pipeline.add_step(get_dummies)

        # Run the feature engineering pipeline to prepare for model training
        train_df = pipeline.run(pd.read_csv('./test/data/ames/train.csv'))

        # Remember the full set of engineered columns we need to produce for the model
        pipeline.set_context('columns', train_df.columns.tolist())

        # Model training, validation and experimentation
        def train(x, y, **kwargs):
            alphas = kwargs.get('alphas', [1, 0.1, 0.001, 0.0001])

            # Select alogrithm
            mtype = kwargs.get('model_type')
            if mtype == 'Lasso':
                model = LassoCV(alphas=alphas)
            elif mtype == 'Ridge':
                model = RidgeCV(alphas=alphas)
            elif mtype == 'ElasticNet':
                model = ElasticNetCV(alphas=alphas)
            else:
                model = LinearRegression()

            # Train model
            model.fit(x, y)
            
            return model

        def predict_and_score(model, x, y):
            predictions = model.predict(x)
            rmse = np.sqrt(mean_squared_error(predictions, y))
            return [predictions, rmse]

        X_train, X_test, y_train, y_test = train_test_split(train_df, y.values, test_size=0.20, random_state=10)

        # adding these to get past errors in experiment mgmt
        train_df.name = 'kaggle/ames-housing-train'
        pipeline._ds = train_df

        # Experiment Mangement

        best_model = None
        best_model_type = None
        best_rmse = 1.0

        exp = cortex.experiment('kaggle/ames-housing-regression')
        exp.set_pipeline(pipeline)
        exp.set_meta('style', 'supervised')
        exp.set_meta('function', 'regression')

        with exp.start_run() as run:
            alphas = [1, 0.1, 0.001, 0.0005]
            for model_type in ['Linear', 'Lasso', 'Ridge', 'ElasticNet']:
                model = train(X_train, y_train, model_type=model_type, alphas=alphas)
                [predictions, rmse] = predict_and_score(model, X_train, y_train)
                [predictions, rmse] = predict_and_score(model, X_test, y_test)
                
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = model
                    best_model_type = model_type
            
            r2 = best_model.score(X_test, y_test)

            run.log_metric('r2', r2)
            run.log_metric('rmse', best_rmse)
            run.log_param('model_type', best_model_type)
            run.log_param('alphas', alphas)
            run.log_artifact('model', best_model)
