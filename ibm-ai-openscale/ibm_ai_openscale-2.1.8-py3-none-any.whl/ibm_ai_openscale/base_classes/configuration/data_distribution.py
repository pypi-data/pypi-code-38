# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
import datetime


class DataDistribution:
    def __init__(self, ai_client, subscription, monitor_definition_id):
        self._ai_client = ai_client
        self._subscription = subscription
        self.monitor_definition_id = monitor_definition_id

    def _prepare_result(self, result, format, group, agg):
        if format == "pandas":
            import pandas as pd
            return pd.DataFrame.from_records(result['values'], columns=result['fields'])
        elif format == 'python':
            return result
        elif format == 'bokeh':
            if len(agg) > 1:
                print('Warning! More aggregations defined than one - in such situation first of them will be taken into consideration preparing data')

            agg_idx = result['fields'].index(agg[0])

            first_col = []
            [first_col.append(row[0]) for row in result['values'] if row not in first_col]
            prepared_res = {
                result['fields'][0]: first_col
            }

            if len(group) == 2:
                second_col = []
                [second_col.append(row[1]) for row in result['values'] if row not in second_col]

                for value2 in second_col:
                    prepared_res[value2] = [res[0][agg_idx] if len(res) > 0 else 0.0 for value1 in first_col for res in [list(filter(lambda x: x[0] == value1 and x[1] == value2, result['values']))]]

                return prepared_res
            elif len(group) == 1:
                prepared_res[agg[0]] = [ row[agg_idx] for row in result['values']]
                return prepared_res
            else:
                raise ClientError('\'bokeh\' format supported only for group with 1 or 2 elements')
        else:
            raise ClientError('Unsupported format: {}'.format(format))

    def run(self, group, start_date=None, end_date=None, filter=None, agg=None, limit=None, max_bins=None,
                              background_mode=False):
        """
        Returns data distribution based on input parameters. By default the format is 'pandas'.

        :param start_date: start datetime in ISO format (optional)
        :type start_date: str

        :param end_date: end datetime in ISO format (optional)
        :type end_date: str

        :param group: names of columns to be grouped
        :type group: list

        :param filter: filters defined by user in format as described in Rest API documentation, example: "Age:eq:33,Gender:in:[F,M]"
        :type filter: str or list of str

        :param agg: aggregation functions in format as described in Rest API documentation, example: ["Age:min", "Age:max", "count"].
                    Supported agg functions are: sum, min, max, avg, stddev, count.
        :type agg: list of str

        :param max_bins: maximum number of bins
        :type max_bins: int

        :param limit: maximal number of fetched rows (optional)
        :type limit: int

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        A way you might use me is:

        >>> data_distribution = subscription.payload_logging.data_distribution.run(start_date='2019-02-26T10:00:00.000Z',
        >>>                                                    end_date='2019-03-26T10:00:00.000Z',
        >>>                                                    group=['AGE', 'GENDER'])
        """

        if start_date is None:
            subscription_details = self._subscription.get_details()
            start_date = subscription_details['metadata']['created_at']

        if end_date is None:
            end_date = datetime.datetime.utcnow().isoformat() + "Z"

        payload = {
            "dataset": self.monitor_definition_id,
            "start": start_date,
            "end": end_date,
            "group": group
        }

        if limit is not None:
            payload['limit'] = limit

        if filter is not None:
            if type(filter) == str:
                payload['filter'] = filter
            elif type(filter) == list:
                payload['filter'] = ','.join(filter)

        if max_bins is not None:
            payload['max_bins'] = max_bins

        if agg is not None:
            payload['agg'] = agg

        response = requests_session.post(
            self._ai_client._href_definitions.get_data_distributions_href(self._subscription.binding_uid,
                                                                  self._subscription.uid),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        result = handle_response(202, u'data distribution run', response)

        request_id = result['id']

        if background_mode:
            return result

        def check_state():
            details = self.get_run_details(request_id)
            return details['status']

        def get_result():
            details = self.get_run_details(request_id)
            state = details['status']

            if state in ['completed']:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['error']), details

        return print_synchronous_run(
            'Waiting for end of data distribution run {}'.format(request_id),
            check_state,
            get_result=get_result,
            success_states=['completed'],
            failure_states=['failed']
        )

    def get_run_details(self, run_id):
        """
        Returns details of run.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str

        :return: details of run
        :rtype: str
        """

        response = requests_session.get(self._ai_client._href_definitions.get_data_distribution_href(self._subscription.binding_uid, self._subscription.uid, run_id),
            headers = self._ai_client._get_headers())

        return handle_response(200, u'data distribution run details', response)

    def get_run_result(self, run_id, format='pandas'):
        """
        Returns data_distribution in chosen format.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str

        :param format: format of returned content, may be one of following: ['python', 'pandas', 'bokeh'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :return: data distribution result
        :rtype: pandas or dict depending on chosen format
        """
        details = self.get_run_details(run_id)
        if details['status'] == 'completed':
            return self._prepare_result(details['distribution'], format, details['group'], details['agg'])
        else:
            raise ClientError('Run status is not completed: {}'.format(details['status']))

    def show_chart(self, run_id):
        """
        Show stacked bars plot for data distribution with up to 2 elements in group. Only available in notebook.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str
        """
        if is_ipython():
            import pandas as pd
            details = self.get_run_details(run_id)
            if details['status'] == 'completed':
                bokeh_result = self._prepare_result(details['distribution'], 'bokeh', details['group'], details['agg'])
            else:
                raise ClientError('Run status is not completed: {}'.format(details['status']))

            pandas_bokeh = pd.DataFrame.from_dict(bokeh_result)
            first_col_name = details['distribution']['fields'][0]

            if len(details['group']) == 2:
                return pandas_bokeh.set_index(first_col_name).groupby(first_col_name).mean().plot.bar(stacked=True)
            else:
                first_agg_name = details['agg'][0]
                return pandas_bokeh.plot.barh(x=first_col_name, y=first_agg_name)
        else:
            raise ClientError("Not a notebook environment.")
