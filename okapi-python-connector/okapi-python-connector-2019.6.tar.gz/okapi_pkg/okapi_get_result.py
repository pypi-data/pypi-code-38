import requests


def okapi_get_result(picard_login, request, url_endpoint,
                     generic_or_not = 'not'):
    # OkapiGetResult() Get results from Picard
    #
    #   Inputs
    #       picard_login - Dict, containing at least URL, options and Token for
    #       Picard. Can be obtained using OkapiInit().
    #       request - dict containing the request_id
    #       url_endpoint - adress, from which the results shall be retrieved
    #       generic_or_not - flag indicating if generic result shall be
    #                        retrieved. Optional, use 'generic' if you want that
    #
    #   Outputs
    #       results - dict, containing the results from the request
    #       error - Dict containing error information. Always check
    #               error['status'] If it is 'FATAL' something went very wrong,
    #               'WARNING's are less critical and 'NONE' or 'INFO' are no
    #               concern. error['message'] gives some explanation on the
    #               status, error['web_states'] gives the http response.

    # init
    result = dict()
    result_dict = dict()
    error = dict()
    error['message'] = 'NONE'
    error['status'] = 'NONE'
    error['web_status'] = 0

    # check the input
    if not('id' in request):
        error['message'] = 'Request was empty or incomplete.'
        error['status'] = 'FATAL'
        error['web_status'] = 204
        return result, error

    if ( generic_or_not == 'generic' ):
        url = picard_login["url"] + url_endpoint + '/' + str(request["id"]) + '/generic'
    else:
        url = picard_login["url"] + url_endpoint + '/' + str(request["id"])

    try:
        result["service"] = url_endpoint
        response = requests.get(url, headers=picard_login["header"], timeout=5)

        # raise for status!
        response.raise_for_status()

        # extract result and stuff: Loop over all objects in the list that was
        # nicely provided to us
        result = response.json()
        i = 0

        # did we try to get a generic result?
        if (generic_or_not == 'generic'):

            error['status'] = result['okapi_output']['status']['content']['type']
            error['message'] = result['okapi_output']['status']['content']['text']

        else:

            while i < len(result):
                # Get the state msgs and stuff
                current_result_dict = result[i]
                if ('state_msg' in current_result_dict):
                    state_msg = current_result_dict['state_msg']
                    error['status'] = state_msg['type']
                    error['message'] = state_msg['text']
                elif('state_msgs' in current_result_dict):
                    state_msgs = current_result_dict['state_msgs']
                    # go through all the messages, check if there is fatal
                    j = 0
                    while j < len(state_msgs):
                        state_msgs_temp = state_msgs[j]
                        error['status'] = state_msgs_temp['type']
                        error['message'] = state_msgs_temp['text']
                        j += 1

                i += 1

        error['web_status'] = response.status_code

        # Finally: Check, if status is 202 which means "results might not be
        # complete"
        if ((response.status_code == 202) and (error['status'] != 'FATAL')):
            error['status'] = 'WARNING'
            error['message'] = 'Result has been accepted but not been fully processed yet.'

    except requests.exceptions.HTTPError:

        # need to get the response from the result to send the error
        try:
            result = response.json()
            result_dict = result[0]
        except:
            result = dict()
            result_dict = dict()

        if ('state_msg' in result_dict):
            state_msg = result_dict['state_msg']
            error['status'] = state_msg['type']
            error['message'] = state_msg['text']
        elif('state_msgs' in result_dict):
            result_dict = result[1]
            state_msgs = result_dict['state_msgs']

            state_msgs_temp = state_msgs[0]
            error['status'] = state_msgs_temp['type']
            error['message'] = state_msgs_temp['text']

        error['web_status'] = response.status_code
        return result, error
    except requests.exceptions.Timeout:
        error['message'] = 'Got timeout when sending request. '
        error['status'] = 'FATAL'
        error['web_status'] = 408
        return result, error
    except requests.exceptions.RequestException:
        error['message'] = 'Got unknown exception. '
        error['status'] = 'FATAL'
        error['web_status'] = 520  # non-standard
        return result, error

    return result, error
