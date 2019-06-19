# -*- coding: utf-8 -*-
try:
    import constants
except ImportError:
    from test_report_processor import constants
import collections
import datetime
import json
import re

import requests


class CucumberReport:
    """JSON cucumber input"""
    def __init__(self, file_location):
        self.features = self.import_pytest_features(file_location)

    def import_pytest_features(self, file_location):
        with open(file_location, 'r') as root:
            cucumber_dict = json.load(root)
            features = []
            for feature in cucumber_dict:
                feature['elements'] = self.filter_out_reruns(feature['elements'])
                feature_dict = {
                    'feature_name': str(feature['name']),
                    'feature_description': feature['description'],
                    'amount_scenarios': len(feature['elements']),
                    'scenarios': [],
                    'tags': [tag['name'] for tag in feature['tags']],
                }
                for scenario in feature['elements']:
                    scenario_dict = {
                        'id': str(scenario['id']),
                        'name': scenario['name'],
                        'description': scenario['description'],
                        'tags': [tag['name'] for tag in scenario['tags']],
                    }
                    steps_list = []
                    for step in scenario['steps']:
                        error_message = step['result'].get('error_message', '')
                        error_message = re.sub('[\'\"]+', '', error_message)
                        step_dict = {
                            'name': "{} {}".format(step['keyword'], step['name']),
                            'status': step['result']['status'].title(),
                            'duration': int(step['result']['duration'] / 1000000),
                            'error_message': error_message,
                        }
                        steps_list.append(step_dict)
                    scenario_dict['steps'] = steps_list
                    scenario_dict['status'] = self.get_scenario_status(scenario_dict)
                    scenario_dict['duration'] = self.get_scenario_duration(scenario_dict)
                    feature_dict['scenarios'].append(scenario_dict)
                features.append(feature_dict)
            return features

    def filter_out_reruns(self, input_scenarios):
        all_feature_scenario_names = [scenario['id'] for scenario in input_scenarios]
        duplicate_scenario_names = [
            item for item, count in collections.Counter(all_feature_scenario_names).items()
            if count > 1
        ]
        unduplicate_scenarios = [
            scenario for scenario in input_scenarios
            if scenario['id'] not in duplicate_scenario_names
        ]

        for duplicate_name in duplicate_scenario_names:
            result = [scenario for scenario in input_scenarios if scenario['id'] == duplicate_name][-1]
            unduplicate_scenarios.append(result)
        return unduplicate_scenarios

    def get_scenario_status(self, scenario):
        status = "Passed"
        for step in scenario['steps']:
            if step['status'] != "Passed":
                status = "Failed"
        return status

    def get_scenario_duration(self, scenario):
        duration = 0
        for step in scenario['steps']:
            duration += int(step['duration'])
        return duration


class PaesslerReport:
    """JSON Paessler output"""
    def __init__(self,
                 scenario,
                 unit_label,
                 unit_warning,
                 unit_error,
                 sensor_dict,
                 paessler_url):
        self.scenario = scenario
        self.prtg_url = paessler_url + "/"
        with open(sensor_dict, "r") as sensor_list:
            self.sensor_dict = json.load(sensor_list)

        self.unit_label = unit_label
        self.unit_warning = unit_warning
        self.unit_error = unit_error

    def get_paessler_dict(self):
        steps_array = []
        if 'paessler' in self.scenario['tags']:
            for step in self.scenario['steps']:
                channel_name = step['name']
                step_status = {
                    'channel': channel_name,
                    'customunit': self.unit_label,
                    'limitmode': 1,
                    'limitmaxwarning': self.unit_warning,
                    'limitmaxerror': self.unit_error,
                    'value': 1
                }
                if step['status'] != "Passed":
                    step_status['value'] = int(self.unit_error) + 1
                if self.unit_label == "ms":
                    step_status['value'] = step["duration"]
                steps_array.append(step_status)
        paessler_dict = {
            'prtg': {
                'result': steps_array
            }
        }
        return paessler_dict

    def get_paessler_url(self, sensor_key):
        if sensor_key in self.sensor_dict:
            return str(self.prtg_url + self.sensor_dict[sensor_key])
        else:
            return


class ReportParser:
    """Cucumber Report JSON parser"""
    def __init__(
        self,
        report_location,
        export_type,
        unit_label="status",
        unit_warning="2",
        unit_error="4",
        sensor_dict="paessler_sensor_dict.json",
        paessler_url="https://10.64.95.34:4001",
        jenkins_url=None,
    ):

        self.paessler_label = unit_label
        self.paessler_warning = unit_warning
        self.paessler_error = unit_error
        self.sensor_dict = sensor_dict
        self.paessler_url = paessler_url
        self.slack_webhook = constants.slack_webhook

        cucumber_report = CucumberReport(report_location)
        self.result = self.parse_report(cucumber_report, jenkins_url, export_type)

    def parse_report(self, cucumber_report, jenkins_url, export_type):
        if export_type == 'paessler':
            return self.parse_paessler_report(cucumber_report)

        elif export_type == 'smashing':
            return self.parse_smashing_report(cucumber_report)

        elif export_type == 'slack':
            return self.parse_slack_report(cucumber_report, jenkins_url)

    def parse_slack_report(self, cucumber_report, jenkins_url):
        slack_results = []
        failed_scenarios = []

        for feature in cucumber_report.features:
            slack_payload_template = {
                'title': 'title',
                'username': 'MijnKPN monitoring',
                'icon_url': 'https://docs.pytest.org/en/latest/_static/pytest1.png',
            }

            attachment_template = {
                'fallback': 'MijnKPN pytest monitoring',
                'color': '#FF0000',
                'title_link': jenkins_url,
            }

            scenarios = feature['scenarios']
            fields = []
            old_feature = []
            for scenario in scenarios:
                failed_step = [test_step for test_step in scenario['steps'] if test_step['status'] == 'Failed']
                if len(failed_step) > 0:
                    failed_scenarios.append(scenario['name'])

                    fields.append({
                        'short': False,
                        'title': 'Scenario "{}" failed'.format(scenario['name']),
                    })
                    if feature != old_feature:
                        attachment = attachment_template.copy()
                        attachment['fields'] = fields
                        attachment['title'] = 'Feature: "{}" failed.'.format(
                            feature['feature_name'])
                        slack_payload = slack_payload_template.copy()
                        slack_payload['attachments'] = [attachment]
                        slack_results.append(slack_payload)
                        old_feature = feature

            if not failed_scenarios:
                field = [{
                    'short': True,
                    'title': '0 Failed tests',
                }]
                attachment = attachment_template.copy()
                attachment['fields'] = field
                attachment['title'] = 'All test cases passed'
                attachment['color'] = "#36A64F"

                slack_payload = slack_payload_template.copy()
                slack_payload['attachments'] = [attachment]
                slack_results.append(slack_payload)
        return slack_results

    def parse_smashing_report(self, cucumber_report):
        smashing_results = {
            'auth_token': 'YOUR_AUTH_TOKEN',
            'last_updated': datetime.datetime.now().strftime('last run: %d-%m-%Y - %H:%M'),
            'timing': [],
        }
        feature_result_list = {}
        for feature in cucumber_report.features:
            failed = 0
            for scenario in feature['scenarios']:
                if 'smashing' in scenario['tags'] or 'smashing' in feature['tags']:
                    if len([step for step in scenario['steps'] if step['status'] != "Passed"]):
                        failed += 1
            if feature['feature_name'] not in feature_result_list:
                feature_result_list[feature['feature_name']] = failed
            else:
                feature_result_list[feature['feature_name']] += failed
        for key, value in self.get_dict_items(feature_result_list):
            status = 'Passed'
            if value > 0:
                status = 'Failed'
            smashing_results['timing'].append({'name': key, 'status': status})
        return smashing_results

    def filter_smashing_column(self, smashing_json, feature_list):
        filtered_features = [result for result in smashing_json['timing'] if result['name'] in feature_list]
        return {
            'auth_token': 'YOUR_AUTH_TOKEN',
            'last_updated': datetime.datetime.now().strftime('last run: %d-%m-%Y - %H:%M'),
            'timing': filtered_features,
        }

    def get_dict_items(self, input_dict):
        try:
            items = input_dict.iteritems()
        except AttributeError:
            items = input_dict.items()
        return items

    def parse_paessler_report(self, cucumber_report):
        paessler_results = []
        for feature in cucumber_report.features:
            for scenario in feature['scenarios']:
                paessler_report = PaesslerReport(
                    scenario,
                    self.paessler_label,
                    self.paessler_warning,
                    self.paessler_error,
                    self.sensor_dict,
                    self.paessler_url,
                )

                sensor_key = self.get_paessler_sensor_id(scenario['id'])
                url = paessler_report.get_paessler_url(sensor_key)
                paessler_json = paessler_report.get_paessler_dict()
                if url and paessler_json:
                    paessler_results.append({
                        'paessler_url': url,
                        'paessler_json': paessler_json,
                    })
        return paessler_results

    def get_paessler_sensor_id(self, scenario_id):
        return scenario_id[5:]

    def report_to_paessler(self, paessler_results):
        for result in paessler_results:
            paessler_url = result.get('paessler_url')
            paessler_json = result.get('paessler_json')
            if paessler_url and paessler_json and paessler_url != "":
                output_json = json.dumps(paessler_json)
                result = requests.get(url=paessler_url, params=dict(content=output_json), verify=False)
                print(result.text)

    def report_to_smashing(self, smashing_json, widget_name, url="http://localhost:3030"):
        json_result = json.dumps(smashing_json)
        requests.post(url + "/widgets/{}".format(widget_name), data=json_result, verify=False)

    def report_to_slack(self, slack_payloads):
        for payload in slack_payloads:
            requests.post(self.slack_webhook, json=payload)
