import requests
import time


def okapi_init(url, username, password):
    # okapi_init() Performs the login and initialization. By default, all
    # possible scopes are requested.
    #
    # Inputs:
    #     url - The url, where OKAPI is running.
    #     username - the username to access OKAPI_Orbits' services
    #     password - the password to access OKAPI_Orbits' services
    #
    # Outputs:
    #     okapi_login - Dict, containing URL, Token, accessTime and options.
    #                   Send to all other routines. NOTE: Is valid for 1 day
    #     error - Dict containing error information. Always check
    #             error['status'] If it is 'FATAL' something went very wrong,
    #             'WARNING's are less critical and 'NONE' or 'INFO' are no
    #             concern. error['message'] gives some explanation on the
    #             status, error['web_states'] gives the http response.
    #

    # init
    error = dict()
    okapi_login = dict()
    error['message'] = 'NONE'
    error['status'] = 'NONE'
    error['web_status'] = 0

    request_token_payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "audience": "https://api.okapiorbits.space/picard",
        "scope": ('neptune_propagation neptune_propagation_request '
                  'pass_predictions pass_prediction_requests '
                  'pass_predictions_long pass_prediction_requests_long'),
        "client_id": "jrk0ZTrTuApxUstXcXdu9r71IX5IeKD3",
    }

    try:
        url_auth = "https://okapi-development.eu.auth0.com/oauth/token"
        okapi_login_token_response = requests.post(url_auth,
                                                   data=request_token_payload,
                                                   timeout=5)
        okapi_login_token_response.raise_for_status()
        okapi_login_token = okapi_login_token_response.json()

        okapi_login = {
            "token": okapi_login_token,
            "url": url,
            "accessTime": str(time.time()),
            "header": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "access_token": okapi_login_token["access_token"],
                "expires_in": str(okapi_login_token["expires_in"]),
                "token_type": okapi_login_token["token_type"],
                "scope": okapi_login_token["scope"]
            }
        }

    except requests.exceptions.HTTPError as err:
        print(err)
        # we now that 403 is probably wrong password:
        if (okapi_login_token_response.status_code == 403):
            response = okapi_login_token_response.json()
            error['message'] = ('Got error from Auth0: ' + response['error'] +
                                ': ' + response['error_description'])
            error['status'] = 'FATAL'
            error['web_status'] = okapi_login_token_response.status_code
        else:
            error['message'] = 'Got HTTPError when sending request. '
            error['status'] = 'FATAL'
            error['web_status'] = okapi_login_token_response.status_code
        return okapi_login, error
    except requests.exceptions.Timeout as err:
        print(err)
        error['message'] = 'Got timeout when sending request. '
        error['status'] = 'FATAL'
        error['web_status'] = 408  # correct timeout?
        return okapi_login, error
    except requests.exceptions.RequestException as err:
        print(err)
        error['message'] = 'Got unknown exception. '
        error['status'] = 'FATAL'
        error['web_status'] = 520  # non-standard
        return okapi_login, error

    return okapi_login, error
