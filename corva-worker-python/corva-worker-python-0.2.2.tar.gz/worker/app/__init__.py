import json
import time

from worker.app.modules.time_activity_module import TimeActivityModule
from worker.framework import constants
from worker.data.operations import gather_wits_for_period
from worker.framework.mixins import RedisMixin, LoggingMixin, RollbarMixin
from worker.framework.state import State
from worker import exceptions


class App(RedisMixin, LoggingMixin, RollbarMixin):
    app_state_fields = {
        'asset_id': int,
        'last_processed_timestamp': int
    }

    def __init__(self, *args, **kwargs):
        self.init_logging()
        self.init_rollbar(*args, **kwargs)

        self.asset_id = None
        self.event = None
        self.state = None

        self.app_name = constants.get('global.app-name')
        self.app_key = constants.get('global.app-key')

    def load(self, event: str):
        """
        :param event: a scheduler event or wits stream
        :return:
        """
        event_type = self.get_event_type()
        event = self.clean_event(event)

        self.asset_id = self.determine_asset_id(event)
        self.state = self.load_state()

        max_lookback_seconds = self.get_max_lookback_seconds()
        self.event = self.load_event(event_type, event, max_lookback_seconds)
        self.log_event(self.event, max_lookback_seconds)

    def log_event(self, event, max_lookback_seconds):
        self.debug(self.asset_id, "WITS input to {0} -> {1}".format(self.app_name, event))
        batch_size = len(event)
        start_time = event[0].get("timestamp")
        end_time = event[-1].get("timestamp")
        system_time = time.time()

        self.log(
            self.asset_id,
            "Received {} elements from {} to {} at {}. {} seconds of initial data are lookback.".format(
                batch_size, start_time, end_time, system_time, max_lookback_seconds
            )
        )

    @staticmethod
    def get_event_type():
        event_type = constants.get('global.event-type', "")

        if event_type not in ("scheduler", "wits_stream"):
            raise Exception('event_type specified incorrectly: {}'.format(event_type))

        return event_type

    @staticmethod
    def clean_event(event):
        if not event:
            raise Exception("Empty event")

        try:
            event = json.loads(event)
        except ValueError:
            raise Exception("Invalid event JSON")

        return event

    def get_max_lookback_seconds(self):
        """
        For each module (mostly in time-base modules), the time of processing does not
        match the last time of the event so extra data is required to look back and get
        the data so the processing can start from where it left off.
        :return:
        """

        time_modules = [module for module in self.get_modules() if issubclass(module, TimeActivityModule)]
        maximum_lookback = 0
        for module in time_modules:
            module_lookback = constants.get('{}.{}.export-duration'.format(self.app_key, module.module_key), default=0)
            maximum_lookback = max(module_lookback, maximum_lookback)

        return maximum_lookback

    def load_event(self, event_type, event, max_lookback_seconds):
        if event_type == 'scheduler':
            return self.load_scheduler_event(self.asset_id, event, max_lookback_seconds)

        if event_type == 'wits_stream':
            return self.load_wits_stream_event(self.asset_id, event)

        return None

    def load_scheduler_event(self, asset_id, event, max_lookback_seconds):
        """
        To load a scheduler event and get the wits stream data
        :param asset_id: The asset to load
        :param event: The cleaned event from Kafka scheduler stream
        :param max_lookback_seconds: Maximum amount of time to look back prior to the scheduler event to cover gaps
        :return: list of WITS data between the last processed timestamp and the final event item timestamp
        """

        event = self.format_scheduler_event(event)
        start_timestamp = self.state.get('last_processed_timestamp', event[0].get('timestamp'))
        end_timestamp = event[-1].get('timestamp', start_timestamp)

        # the event is converted from scheduler to wits stream
        scheduler_event = gather_wits_for_period(
            asset_id=asset_id,
            start=start_timestamp - max_lookback_seconds,
            end=end_timestamp,
            limit=constants.get('global.query-limit'))

        return scheduler_event

    @staticmethod
    def format_scheduler_event(event: list) -> list:
        """
        validate the scheduler event, flatten and organize the data into a desired format
        :param event: a scheduler event
        :return: a dict structured in such a way that the key is asset_id and
        the value is the wits records that belong to that asset_id
        """

        flat_events = []

        try:
            # Because the events are structured into 'list of lists', using the following code
            # converts them into a flat single list. This is done for better data processing in
            # the proceeding steps.
            flat_events = [item for sublist in event for item in sublist]
        except ValueError:
            raise Exception("Records are not valid JSON: {0}...".format(str(flat_events)[:100]))

        if not isinstance(flat_events, list):
            raise Exception("Records is not an array: {0}".format(flat_events))

        if not flat_events:
            raise Exception("Records is empty.")

        events = [
            {
                "asset_id": item["asset_id"],
                "timestamp": int(item['schedule_start'] / 1000)
            }
            for item in flat_events
        ]

        return events

    def load_wits_stream_event(self, asset_id, event, max_lookback_seconds):
        """
        To load a wits stream event and get more data if necessary
        :param asset_id: The asset to load
        :param event: The cleaned event from Kafka WITS stream
        :param max_lookback_seconds: Maximum amount of time to look back prior to WITS data to cover gaps
        :return: list of WITS data between the first event timestamp and the first timestamp
        """

        if event and max_lookback_seconds:
            first_timestamp = self.event[0].get('timestamp')

            if not first_timestamp:
                return event

            # Subtract one from the timestamp so that we don't reselect the final data item that was sent in the event
            end_timestamp = first_timestamp - 1

            previous_events = gather_wits_for_period(
                asset_id=asset_id,
                start=first_timestamp - max_lookback_seconds,
                end=end_timestamp,
                limit=constants.get('global.query-limit'))

            event = previous_events + event

        return event

    @staticmethod
    def determine_asset_id(event: list) -> int:
        try:
            return int(event[0][0]["asset_id"])
        except Exception:
            raise Exception('Event does not contain asset_id: {}'.format(event))

    def load_state(self):
        try:
            r = self.get_redis()
            previous_state = r.get(self.get_redis_key(self.asset_id, self.app_key))
            previous_state = json.loads(previous_state)
        except Exception as ex:
            self.error(self.asset_id, "REDIS connection error: {0}".format(ex))
            previous_state = {
                "asset_id": self.asset_id,
            }

        state = State(self.app_state_fields, previous_state)

        if not state.get('asset_id', None):
            state['asset_id'] = self.asset_id

        return state

    def save_state(self):
        r = self.get_redis()
        r.set(self.get_redis_key(self.asset_id, self.app_key), value=self.state.to_json())

    def get_modules(self):
        raise exceptions.Misconfigured("No modules found")

    def run_modules(self):
        for module_type in self.get_modules():
            try:
                module = module_type(self.state)
            except Exception:
                raise exceptions.Misconfigured("Module not able to initialize {0}".format(module_type))

            try:
                module.run(self.event)
            except Exception:
                self.track_error("Error running module {0} for asset:{1}".format(module_type, self.asset_id), "error")

        last_processed_timestamp = self.event[-1].get('timestamp')
        self.state['last_processed_timestamp'] = last_processed_timestamp
