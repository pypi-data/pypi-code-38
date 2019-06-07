# coding=utf-8
import os
import datetime
import random
import json
import pandas as pd
from io import StringIO
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale.supporting_classes import BluemixCloudObjectStorageReference
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale.supporting_classes import MeasurementRecord
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
from ibm_ai_openscale_cli.database_classes.cos import CloudObjectStorage
from pathlib import Path

logger = FastpathLogger(__name__)

class Model():

    CONFIGURATION_FILENAME = 'configuration.json'
    MODEL_META_FILENAME = 'model_meta.json'
    MODEL_CONTENT_FILENAME = 'model_content.gzip'
    PIPELINE_META_FILENAME = 'pipeline_meta.json'
    PIPELINE_CONTENT_FILENAME = 'pipeline_content.gzip'
    TRAINING_DATA_STATISTICS_FILENAME = 'training_data_statistics.json'
    FAIRNESS_HISTORY_FILENAME = 'history_fairness.json'
    PAYLOAD_HISTORY_FILENAME = 'history_payloads.json'
    TRAINING_DATA_CSV_FILENAME = 'training_data.csv'
    FEEDBACK_CSV_FILENAME = 'feedback_data.csv'
    DEBIAS_HISTORY_FILENAME = 'history_debias.json'
    QUALITY_HISTORY_FILENAME = 'history_quality.json'
    QUALITY_MONITOR_HISTORY_FILENAME = 'history_quality_monitor.json'
    MANUAL_LABELING_HISTORY_FILENAME = 'history_manual_labeling.json'
    PERFORMANCE_HISTORY_FILENAME = 'history_performance.json'

    def __init__(self, name, args, model_instances=1):
        self._args = args
        self.name = name
        if model_instances > 1:
            self.name += str(model_instances)

        if self._args.custom_model_directory:
            self._model_dir = self._args.custom_model_directory
        else:
            self._model_dir = os.path.join(os.path.dirname(__file__), name)
        env_name = '' if self._args.env_dict['name'] == 'YPPROD' else self._args.env_dict['name']

        # model create and deploy
        self.metadata = {}
        if self._args.custom_model: # don't add env to model name if this is a custom model
            self.metadata['model_name'] = self.name
        else:
            self.metadata['model_name'] = self.name + env_name
        self.metadata['model_metadata_file'] = self._get_file_path(Model.MODEL_META_FILENAME)
        self.metadata['model_file'] = self._get_file_path(Model.MODEL_CONTENT_FILENAME)
        self.metadata['pipeline_metadata_file'] = self._get_file_path(Model.PIPELINE_META_FILENAME)
        self.metadata['pipeline_file'] = self._get_file_path(Model.PIPELINE_CONTENT_FILENAME)
        if self._args.deployment_name: # if this is an existing deployment use the name provided
            self.metadata['deployment_name'] = self._args.deployment_name
        elif self._args.custom_model: # don't add env to deployment name if this is a custom model
            self.metadata['deployment_name'] = self.name
        else:
            self.metadata['deployment_name'] = self.name + env_name
        self.metadata['deployment_description'] = 'Created by Watson OpenScale Fast Path.'

        # configuration
        configuration_file = self._get_file_path(Model.CONFIGURATION_FILENAME)
        if configuration_file:
            self.configuration_data = jsonFileToDict(configuration_file)
        else:
            error_msg = 'ERROR: Unable to find configuration file for this model: {}'.format(Model.CONFIGURATION_FILENAME)
            logger.log_error(error_msg)
            raise Exception(error_msg)

        # training data
        training_data_statistics_file = self._get_file_path(Model.TRAINING_DATA_STATISTICS_FILENAME)
        training_data_csv_file = self._get_file_path(Model.TRAINING_DATA_CSV_FILENAME)
        training_data_type = self._get_training_data_type()
        self.training_data_reference = None
        self.training_data = None
        self.training_data_statistics = None
        if 'training_data_reference' in self.configuration_data:
            logger.log_info('Read model training data from IBM Cloud Object Storage')
            self.training_data_reference = self.configuration_data['training_data_reference']
            first_line_header = True if self.training_data_reference['firstlineheader'] == 'true' else False
            self.training_data_reference['cos_storage_reference'] = BluemixCloudObjectStorageReference(
                self.training_data_reference['credentials'],
                self.training_data_reference['path'],
                first_line_header=first_line_header )
            cos = CloudObjectStorage(self.training_data_reference['credentials'])
            training_data_csv = cos.get_file(self.training_data_reference['path'])
            self.training_data = pd.read_csv(StringIO(training_data_csv), dtype=training_data_type)
        elif training_data_statistics_file:
            self.training_data_statistics = jsonFileToDict(training_data_statistics_file)
            if training_data_csv_file:
                self.training_data = pd.read_csv(training_data_csv_file, dtype=training_data_type)
            else:
                error_msg='ERROR: training_data.csv required with training_data_statistics.json'
                logger.log_error(error_msg)
                raise Exception(error_msg)
        else:
            error_msg='ERROR: Unable to find training data'
            logger.log_error(error_msg)
            raise Exception(error_msg)

        # refactor training data for use by online scoring
        self.training_data_columns = {}
        for column_name in self.training_data.columns:
            column = []
            for values in self.training_data[column_name]:
                column.append(values)
            self.training_data_columns[column_name] = column

        # feedback data - uses same dtype as training data
        self.feedback_data = None
        feedback_file = self._get_file_path(Model.FEEDBACK_CSV_FILENAME)
        if feedback_file:
            self.feedback_data = pd.read_csv(feedback_file, dtype=training_data_type).to_dict('records') # make a list-style DICT

    def _get_training_data_type(self):
        training_data_type = None
        if 'training_data_type' in self.configuration_data:
            training_data_type = {}
            for key in self.configuration_data['training_data_type'].keys():
                if self.configuration_data['training_data_type'][key] == 'int':
                    training_data_type[key] = int
                elif self.configuration_data['training_data_type'][key] == 'float':
                    training_data_type[key] = float
        return training_data_type

    def _get_file_path(self, filename):
        """
        Returns the path for the file for the current serve engine, else the common file
        Eg. /path/to/sagemaker/training_data_statistics.json OR /path/to/training_data_statistics.json OR None
        """
        engine_specific_path = os.path.join(self._model_dir, self._args.ml_engine_type.name.lower(), filename)
        if Path(engine_specific_path).is_file():
            return engine_specific_path
        else:
            path = os.path.join(self._model_dir, filename)
            if Path(path).is_file():
                return path
        return None

    def _get_score_time(self, day, hour):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))

    # return an array of tuples with datestamp, response_time, and records
    def get_performance_history(self, num_day):
        """ Retrieves performance history from a json file"""
        fullRecordsList = []
        history_file = self._get_file_path(Model.PERFORMANCE_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                performance_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(performance_values) # wrap around and reuse values if needed
                fullRecordsList.append({'timestamp': score_time, 'value': performance_values[index]})
        return fullRecordsList

    def get_fairness_history(self, num_day):
        """ Retrieves fairness history from a json file"""
        fullRecordsList = []
        history_file = self._get_file_path(Model.FAIRNESS_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                fairness_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(fairness_values) # wrap around and reuse values if needed
                fullRecordsList.append({'timestamp': score_time, 'value': fairness_values[index]})
        return fullRecordsList

    def get_debias_history(self, num_day):
        """ Retrieves debias history from a json file"""
        fullRecordsList = []
        history_file = self._get_file_path(Model.DEBIAS_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                debias_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(debias_values) # wrap around and reuse values if needed
                fullRecordsList.append({'timestamp': score_time, 'value': debias_values[index]})
        return fullRecordsList

    def get_quality_history(self, num_day):
        fullRecordsList = []
        history_file = self._get_file_path(Model.QUALITY_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                quality_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(quality_values) # wrap around and reuse values if needed
                fullRecordsList.append({'timestamp': score_time, 'value': quality_values[index]})
        return fullRecordsList

    def get_quality_monitor_history(self, num_day):
        fullRecordsList = []
        history_file = self._get_file_path(Model.QUALITY_MONITOR_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                quality_values = json.load(f)
            for hour in range(24):
                score_time = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                index = (num_day * 24 + hour) % len(quality_values) # wrap around and reuse values if needed
                quality_value = quality_values[index]
                fullRecordsList.append(MeasurementRecord(metrics=quality_value['metrics'], sources=quality_value['sources'], timestamp=score_time))
        return fullRecordsList

    def get_manual_labeling_history(self, num_day):
        """ Retrieves manual labeling history from a json file"""
        fullRecordsList = []
        history_file = self._get_file_path(Model.MANUAL_LABELING_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                manual_labeling_records = json.load(f)
            for record in manual_labeling_records:
                # use fastpath_history_day value to check to see if this manual labeling history record is in the right range
                # if the value is -1, then the file is just one day's records, to be repeated each day
                if record['fastpath_history_day'] == num_day or record['fastpath_history_day'] == -1:
                    # generate the scoring_timestamp value and then remove the fastpath_history_day/hour values
                    hour = record['fastpath_history_hour']
                    record['scoring_timestamp'] = self._get_score_time(num_day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                    del record['fastpath_history_day']
                    del record['fastpath_history_hour']
                    fullRecordsList.append(record)
        return fullRecordsList

    def get_score_input(self, num_values=1):
        values = []
        for _ in range(num_values):
            value = []
            num_rows = len(self.training_data)
            random_row = random.randint(0, num_rows - 1)
            for field in self.configuration_data['asset_metadata']['feature_columns']:
                if self._args.score_columns: # pick from a different random row for each field
                    random_row = random.randint(0, num_rows - 1)
                value.append(self.training_data_columns[field][random_row])
            values.append(value)
        return (self.configuration_data['asset_metadata']['feature_columns'], values)

    def get_payload_history(self, num_day):
        fullRecordsList = []
        # each 'payload_history_N.json' file contains a full day of payloads, to be divided across 24 hours
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME.replace('.json', ('_' + str(num_day) + '.json')))
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = len(payloads) // 24
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        score_time = str(self._get_score_time(num_day, hour))
                        fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
                        index += 1
            return fullRecordsList

        # the 'payload_history_day.json' file contains a full day of payloads, to be divided across 24 hours
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME.replace('.json', '_day.json'))
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = len(payloads) // 24
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        score_time = str(self._get_score_time(num_day, hour))
                        fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
                        index += 1
            return fullRecordsList

        # the 'payload_history.json' file contains one hour of payloads, to be duplicated for every hour
        history_file = self._get_file_path(Model.PAYLOAD_HISTORY_FILENAME)
        if history_file:
            with open(history_file) as f:
                payloads = json.load(f)
            for hour in range(24):
                for payload in payloads:
                    req = payload['request']
                    resp = payload['response']
                    score_time = str(self._get_score_time(num_day, hour))
                    fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
            return fullRecordsList

        # no payload history provided
        return fullRecordsList
