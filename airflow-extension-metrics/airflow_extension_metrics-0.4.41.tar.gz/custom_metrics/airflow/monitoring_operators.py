from custom_metrics.helpers import get_total_time_dict_from_context, get_point_dict_from_context, get_callback_metric_dict, get_callback_point_dict
from custom_metrics.helpers.stackdriver_metrics import create_descriptor, log_point
from datetime import datetime


def monitor(operator_class, **kwargs):
    # TODO: let's make monitor function accept a `metric_reporter`, which will handle logics performed in `get_labels_for_metric` and `get_labels_for_point`
    # TODO: as well as formatting inputs for Stackdriver and any other potential integrations (can be done with bunch of Handler classes that gets injected into the metric_reporter)
    google_project_name = kwargs.pop('google_project')
    google_location = kwargs.pop('google_location')
    labels = kwargs.pop('labels', [])

    # TODO: figure out how to template fields so they're accessible in callback functions too
    # define arguments that need to be templated here

    class MonitoredOperator(operator_class):

        def __init__(self, **kwargs):

            orig_failure_call = kwargs.pop('on_failure_callback', None)
            orig_retry_call = kwargs.pop('on_retry_callback', None)
            orig_success_call = kwargs.pop('on_success_callback', None)

            failure_callback = self.callback_wrapper(orig_failure_call, 'failure')
            retry_callback = self.callback_wrapper(orig_retry_call, 'retry')
            success_callback = self.callback_wrapper(orig_success_call, 'success')

            kwargs['on_failure_callback'] = failure_callback
            kwargs['on_retry_callback'] = retry_callback
            kwargs['on_success_callback'] = success_callback

            super(MonitoredOperator, self).__init__(**kwargs)

            self.google_project_name = google_project_name
            self.google_location = google_location
            self.labels = labels

            # Make sure we have required kwargs
            if self.google_project_name is None or self.google_location is None:
                raise Exception('Both google_project and google_location need to be provided in the monitored '
                                'operator keyword arguments.')

            # Confirm that if labels are provided, each dictionary in the list has the right structure
            if len(self.labels) != 0:
                for label in self.labels:
                    if type(label) is not dict:
                        raise Exception('Elements in the labels list need to be dictionaries.')
                    for required_key in ['key', 'value', 'description', 'value_type']:
                        if required_key not in label.keys():
                            raise Exception(
                                'The key ' + required_key + ' is not in the provided labels dictionary:\n' + str(label))

        def execute(self, context):
            start_time = datetime.now()
            return_val = super(MonitoredOperator, self).execute(context)
            end_time = datetime.now()

            delta = (end_time - start_time).microseconds

            dag_task_key = '__'.join(context.get('task_instance_key_str').split('__')[:2])
            metric_dict = get_total_time_dict_from_context(self.google_project_name, dag_task_key,
                                                           label_list=self.get_labels_for_metric())
            point_dict = get_point_dict_from_context(self.google_location, delta, dag_task_key,
                                                     label_values=self.get_labels_for_point(context))
            self.log.info(point_dict)

            try:
                metric_output = create_descriptor(metric_dict, self.google_project_name)
                self.log.info(metric_output)
            except:
                self.log.warning(
                    'Metric description could not be created in ' + self.google_project_name + '\n' + str(point_dict))

            try:
                point_output = log_point(point_dict, self.google_project_name)
                self.log.info(point_output)

            except:
                self.log.warning('Point could not be logged to ' + self.google_project_name + '\n' + str(point_dict))

            return return_val

        def callback_wrapper(self, on_callback, callback_type):

            def wrapped_function(context):
                return_val = None

                if on_callback is not None:
                    return_val = on_callback(context)

                dag_task_key = '__'.join(context.get('task_instance_key_str').split('__')[:2])
                metric_dict = get_callback_metric_dict(self.google_project_name,
                                                       label_list=self.get_labels_for_metric())
                point_dict = get_callback_point_dict(self.google_location, callback_type, dag_task_key,
                                                     label_values=self.get_labels_for_point(context))

                try:
                    metric_output = create_descriptor(metric_dict, self.google_project_name)
                    print(metric_output)
                except:
                    print('Metric description could not be created in ' + self.google_project_name + '\n' + str(point_dict))

                try:
                    log_point(point_dict, self.google_project_name)
                except:
                    print ('Point could not be logged to ' + self.google_project_name + '\n' + str(point_dict))

                return return_val

            return wrapped_function

        def get_labels_for_metric(self):
            """
            Example:
            [
                {
                    "key": "run_id",
                    "value_type": "STRING",
                    "description": "The ID of the DAG run."
                }
            ]
            """

            metric_labels = [{k: label_dict.get(k) for k in ['key', 'value_type', 'description']} for label_dict in self.labels]

            metric_labels.append({
                    "key": "run_id",
                    "value_type": "STRING",
                    "description": "The ID of the DAG run."
                })

            return metric_labels

        def get_labels_for_point(self, context):
            """
            :return: Dictionary with label key and value for each label
            Example:
                {
                    "run_id": "012345"
                }
            """

            point_labels = {label_dict.get('key'): label_dict.get('value') for label_dict in self.labels}
            run_id = context.get('run_id')
            formatted_id = run_id.replace("T","").replace("-","").replace(":","").replace(".","").replace("+","").split("_")[-1][:18] if run_id else ''
            point_labels.update({"run_id": formatted_id})
            return point_labels

    MonitoredOperator.__name__ = operator_class.__name__
    return MonitoredOperator(**kwargs)
