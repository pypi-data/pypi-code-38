import json

from itertools import groupby

from worker.data.api import API
from worker.data import operations
from worker.framework import constants
from worker.framework.mixins import LoggingMixin, RedisMixin, RollbarMixin
from worker.framework.state import State


class Module(RedisMixin, LoggingMixin, RollbarMixin):
    """
    This is an abstract base module that needs to be extended by an actual module.
    """
    # module_key is used for redis access and state of this module
    module_key = "module"
    collection = "collection"
    module_state_fields = {}

    def __init__(self, global_state, *args, **kwargs):
        self.init_logging()
        self.init_rollbar(*args, **kwargs)

        self.global_state = global_state
        self.state = None

        self.app_name = constants.get('global.app-name')
        self.app_key = constants.get('global.app-key')

    def run(self, wits_stream: list):
        """
        :param wits_stream: a wits stream event
        :return:
        """
        state = self.load_module_state(wits_stream)
        self.state = self.process_module_state(state)

        dataset = self.load_dataset(wits_stream)

        # this guarantees every group has the same config
        config_grouped_dataset = self.group_data_stream_based_on_config(dataset)

        for group in config_grouped_dataset:
            results = self.check_for_string_change(group)

            if self.should_run_processor(group):
                results = self.run_module(group, results)

            self.save_module_state()
            self.store_output(self.global_state['asset_id'], results)

    @staticmethod
    def group_data_stream_based_on_config(dataset):
        """Group our datasets by the metadata such as drillstring, and then reflatten to be a list of lists
        for processing"""

        groups = groupby(dataset, lambda x: x['metadata'])
        grouped_dataset = [list(dataset) for group, dataset in groups]

        return grouped_dataset

    def should_run_processor(self, event):
        running_string = constants.get("{}.{}.running-string".format(self.app_key, self.module_key))
        if running_string and self.state.get('active_string_type', '') in running_string:
            return True

        return False

    def load_module_state(self, event):
        r = self.get_redis()
        current_state = r.get(self.get_redis_key(self.global_state['asset_id'], self.app_key, self.module_key)) or {}

        if current_state:
            current_state = json.loads(current_state)

        current_state = State(self.module_state_fields, current_state)

        return current_state

    @staticmethod
    def process_module_state(state):
        return state

    def set_state(self, key, value):
        self.state[key] = value

    def save_module_state(self):
        r = self.get_redis()
        r.set(
            self.get_redis_key(self.global_state['asset_id'], self.app_key, self.module_key),
            self.state.to_json()
        )

    def load_dataset(self, event):
        return event

    def run_module(self, dataset, beginning_results):
        raise Exception("Not implemented")

    def check_for_string_change(self, data):
        """
        To check if the active string in the wellbore has been changed and
        export proper text to the output.
        Note that the last_exported_timestamp is not set here.
        Note that all the configs of this data have the same config properties.
        :param data:
        :return:
        """

        previous_string = self.state.get('active_string__id', "")
        running_string = constants.get("{}.{}.running-string".format(self.app_key, self.module_key))
        reset_config = constants.get("{}.{}.reset-config".format(self.app_key, self.module_key))

        if not running_string:
            return []

        if not data:
            return []

        first_wits = data[0]
        drillstring__id = first_wits.get('metadata', {}).get('drillstring', None)
        casing__id = first_wits.get('metadata', {}).get('casing', None)

        if not drillstring__id and not casing__id:
            return []

        if drillstring__id:
            active_string_type = 'drillstring'
            active_string__id = drillstring__id
        elif casing__id:
            active_string_type = 'casing'
            active_string__id = casing__id

        if previous_string == active_string__id:
            return []

        asset_id = int(first_wits.get('asset_id'))
        main_structure = {
            'timestamp': int(first_wits.get('timestamp')),
            'company_id': int(first_wits.get('company_id')),
            'asset_id': asset_id,
            'provider': 'corva',
            'version': 1,
            'collection': self.collection,
            'data': {}
        }
        warning = None
        last_document = None

        if active_string_type in running_string:
            if active_string_type not in reset_config:
                return []
        else:
            message = "This module does not run while {} is the active string in the well.".format(active_string_type)
            warning = {
                'message': message
            }

            if active_string_type not in reset_config:
                # get the last record
                worker = API()
                last_document = worker.get(
                    path="/v1/data/corva", collection=self.collection, asset_id=asset_id,
                    sort="{timestamp: -1}", limit=1,
                ).data[0]

        res = self.configure_output_at_config_change(
            main_structure, active_string_type, active_string__id, warning, last_document
        )

        return [res]

    def configure_output_at_config_change(
        self, main_structure, active_string_type, active_string__id, warning=None, last_document=None
    ):
        extra_elements = self.create_output_for_new_config(active_string_type, active_string__id)
        main_structure['data'] = operations.merge_dicts(main_structure['data'], extra_elements)

        if warning:
            main_structure['data'] = operations.merge_dicts(main_structure['data'], {'warning': warning})

        if last_document:
            main_structure['data'] = operations.merge_dicts(last_document.get('data', {}), main_structure['data'])

        return main_structure

    def create_output_for_new_config(self, active_string_type, active_string__id):
        self.set_state('active_string_type', active_string_type)
        self.set_state('active_string__id', active_string__id)

        if active_string_type == 'drillstring':
            drillstring = operations.get_config_by__id('data.drillstring', active_string__id)
            if drillstring:
                drillstring_number = drillstring.get('data', {}).get('id', None)
                self.set_state('drillstring_number', drillstring_number)
        else:
            self.set_state('drillstring_number', None)

        return self.get_config_properties()

    def get_config_properties(self):
        properties = {
            'active_string_type': self.state.get('active_string_type', ''),
            'active_string__id': self.state.get('active_string__id', ''),
        }

        drillstring_number = self.state.get('drillstring_number', None)
        if drillstring_number:
            properties['drillstring_number'] = drillstring_number

        return properties

    def get_last_exported_timestamp_from_collection(self, asset_id, query=None, less_than=None):
        """
        Query the module collection for this asset_id + module, sorted by timestamp descending,
        limit 1, grab the last item's timestamp. Default to 0 if no records found.
        @asset_id:
        @less_than: the timestamp before which you want to get
        """
        if less_than:
            query = query or ""
            query += "AND{timestamp#lt#%s}" % less_than

        worker = API()
        last_document = worker.get(
            path="/v1/data/corva", query=query, collection=self.collection, asset_id=asset_id,
            sort="{timestamp: -1}", limit=1,
        ).data

        if not last_document:
            return 0

        last_document = last_document[0]
        last_processed_timestamp = last_document.get('timestamp', 0)

        return last_processed_timestamp

    @staticmethod
    def gather_first_wits_timestamp_since(asset_id: int, since: int, activity_fields=None, operator='eq') -> int:
        """
        Query the Wits collection for this asset_id where state in wits_states and timestamp >= since
        """

        query = '{timestamp#%s#%s}' % ('gt', since)

        operator = operator.lower()

        if activity_fields:
            if operator == "eq" and isinstance(activity_fields, list):
                operator = "in"

            if operator in ("in", "nin"):
                if not isinstance(activity_fields, list):
                    activity_fields = [activity_fields]

                # Put each state into a formatted string for querying
                activity_fields = ["'{0}'".format(state) for state in activity_fields]
                activity_fields = "[{0}]".format(",".join(activity_fields))
            else:
                activity_fields = "'{0}'".format(activity_fields)

            query += 'AND{data.state#%s#%s}' % (operator, activity_fields)

        worker = API()
        first_wits_since = worker.get(
            path="/v1/data/corva", collection='wits', asset_id=asset_id, sort="{timestamp: 1}", limit=1, query=query
        ).data

        if not first_wits_since:
            return 0

        first_wits_since = first_wits_since[0]
        first_wits_since_timestamp = first_wits_since.get('timestamp', 0)

        return first_wits_since_timestamp

    @staticmethod
    def gather_maximum_timestamp(event, start, activity_fields):
        """
        get the maximum time stamp of a stream of data
        :param event: a stream of data  that the majority is wits collection
        :param start:
        :param activity_fields:
        :return:
        """
        maximum_timestamp = start
        for data in event:
            if data.get("collection") == "wits" and data.get('data', {}).get('state', None) in activity_fields:
                maximum_timestamp = max(data.get("timestamp", 0), maximum_timestamp)

        return maximum_timestamp

    def gather_minimum_timestamp(self, asset_id: int, event: list):
        minimum = self.get_last_exported_timestamp_from_collection(asset_id)

        if not minimum:
            minimum = event[0]["timestamp"] - 1800

        return minimum

    def gather_collections_for_period(self, asset_id, start, end, query=None):
        limit = constants.get("global.query-limit")

        query = query or ""
        if query:
            query += "AND"

        query += "{timestamp#gte#%s}AND{timestamp#lte#%s}" % (start, end)

        worker = API()
        dataset = worker.get(
            path="/v1/data/corva", collection=self.collection, asset_id=asset_id, query=query,
            sort="{timestamp: 1}", limit=limit,
        ).data

        if not dataset:
            return []

        return dataset

    def store_output(self, asset_id, output):
        """
        to store/post results
        :param asset_id: asset id of the well
        :param output: an array of json objects to be posted
        :return: None
        """

        if not asset_id:
            return

        if not output:
            return

        output = self.format_output(output)

        self.debug(asset_id, "{0} output -> {1}".format(self.module_key, output))

        worker = API()
        worker.post(path="/v1/data/corva", data=output)

    @staticmethod
    def format_output(output):
        output = json.dumps(output)
        return output

    @staticmethod
    def compute_timestep(dataset: list):
        if len(dataset) < 2:
            return None

        timestep = (dataset[-1].get('timestamp') - dataset[0].get('timestamp')) / (len(dataset) - 1)

        return timestep
