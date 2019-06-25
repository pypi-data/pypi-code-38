# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""yaml_keys.py, class for defining yaml keys."""

ScheduleRecurrenceYaml = ['frequency', 'interval', 'start_time', 'time_zone', 'hours', 'minutes', 'time_of_day',
                          'week_days']
ScheduleYaml = ['description', 'pipeline_parameters', 'wait_for_provisioning', 'wait_timeout', 'datastore_name',
                'polling_interval', 'data_path_parameter_name', 'continue_on_step_failure', 'path_on_datastore',
                'recurrence']
