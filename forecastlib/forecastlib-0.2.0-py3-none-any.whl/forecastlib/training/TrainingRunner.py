# Databricks notebook source
# %% Select test/train data

import numpy as np
import pandas as pd
from argparse import Namespace
from azureml.core.model import Model
from azureml.core import Run, Workspace
from forecastlib.training.ForecastTrainer import ForecastTrainer

pd.set_option('display.max_columns', None)

# %%


class TrainingRunner(object):
    def __init__(self, ws: Workspace, prepare_dataset_delegate, args=None):
        self.args = args

        if self.args is None:
            self.args = self.parse_args()
        else:
            self.args = Namespace(**args)

        self.ws = ws
        ds = ws.get_default_datastore()
        ds.download(target_path="./", prefix=self.args.source_file, overwrite=True, show_progress=True)

        blob_data = pd.read_csv(self.args.source_file, delimiter=",")

        blob_data.describe(include='all')

        self.train_data, self.test_data = prepare_dataset_delegate(blob_data)


    def parse_args(self):
        import argparse
        print("Parsing parameters")

        parser = argparse.ArgumentParser()

        parser.add_argument('--batch_size', type=int, dest='batch_size', default=1000, help='batch size for training')

        parser.add_argument('--epochs', type=int, dest='epochs', default=13, help='number of epochs')

        parser.add_argument('--layers', type=int, dest='layers', default=1, help='number of hidden layers')

        parser.add_argument('--nodes', type=int, dest='nodes', default=50, help='number of nodes in one hidden layer')

        parser.add_argument('--dropout', type=float, dest='dropout', default=0.5, help='dropout in hidden layers')

        parser.add_argument('--modelname', type=str, dest='modelname', default="high_sell_known",
                            help='name of the model found in MLservice => Models')

        parser.add_argument('--source_file', type=str, dest='source_file', default="modified_forecast_data.csv",
                            help='Data file on storage')

        parser.add_argument('--features', type=str, dest='features', default="",
                            help='Data file on storage')

        parser.add_argument('--save_threshold', type=float, dest='save_threshold', default=50, help='minimal accuracy needed to save model')


        # parser.add_argument('--learning-rate', type=float, dest='learning_rate', default=0.001, help='learning rate')

        args = parser.parse_args()

        print('Running with batch size:', args.batch_size)
        print('Running with epochs:', args.epochs)
        print('Running with hidden layers:', args.layers)
        print('Running with hidden nodes:', args.nodes)
        print('Running with dropout:', args.dropout)
        print('Running with feature set:', args.features)
        print('Running with modelname:', args.modelname)
        print('Running with source file:', args.source_file)
        print('Running with features:', args.features)
        print('Running with save threshold:', args.save_threshold)

        return args

    # COMMAND ----------

    def run(self):
        accuracy_sampling = 1

        # start an Azure ML run
        run = Run.get_context()

        trainer = ForecastTrainer(
            run.id,
            self.args.batch_size,
            self.args.epochs,
            self.args.nodes,
            self.test_data,
            self.train_data,
            accuracy_sampling,
            self.args.features.split(','),
            self.args.dropout,
            self.args.layers)

        run.log("epochs", self.args.epochs)
        run.log("batch_size", self.args.batch_size)
        run.log("nodes", self.args.nodes)
        run.log("layers", self.args.layers)
        run.log("dropout", self.args.dropout) 
        run.log("feature_set", self.args.features)
        run.log("features_num", len(self.args.features.split(',')))
        run.log("model_name", self.args.modelname)

        lossesIn, accuraciesIn = trainer.train()

        acc = trainer.get_accuracy()
        best_acc = max(accuraciesIn)

        # log a single value
        run.log("best_accuracy", best_acc)
        run.log("final_accuracy", acc)
        print('Accuracy log:', acc)

        print("Inliner acc: ", accuraciesIn)

        # COMMAND ----------

        if acc > self.args.save_threshold:
            path = trainer.save_best_model(self.args.modelname, 'output')

            if self.args.modelname is not None:
                Model.register(
                    workspace=self.ws,
                    model_name=self.args.modelname,
                    model_path=path,
                    properties={"Accuracy": trainer.get_accuracy(), "ModelFit": trainer.get_model_fit()},
                    description="FinalAccuracy: {:.2f} | ModelFit: {:.2f}".format(trainer.get_accuracy(), trainer.get_model_fit())
                )
                print("Model {0} successfully registered to experiment".format(self.args.modelname))
        else:
            print("Accuracy {0} is below defined threshold ({1}), model will NOT be saved".format(acc, self.args.save_threshold))
        run.complete()
