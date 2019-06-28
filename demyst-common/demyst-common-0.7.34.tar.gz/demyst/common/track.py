import requests
import time
import sys

# Call function.  If it succeeds, send normal Pendo event and return
# its result. If it fails, send event error_message property set to
# exception message.
def track_function(fn, config, event_name, properties=None):
    if properties is None:
        properties = {}
    try:
        result = fn()
        pendo(config, event_name, properties)
        return result
    except Exception as e:
        properties["error_message"] = str(e)
        pendo(config, event_name + " : Error", properties)
        raise e

def pendo(config, event_name, properties=None):
    if properties is None:
        properties = {}
    # Don't track non-production environments
    if (config.get("ENV") != "prod"):
        return
    timestamp = int(round(time.time() * 1000))

    if config.has("API_KEY"):
        email = config.get("API_KEY")[:8]
        account_id = "API key users"
        user_id = config.get("API_KEY")[:8]
        user_fullname = "API key user"
    else:
        email = config.get_username()
        account_id = config.get_organization()
        user_id = config.get_console_userid()
        user_fullname = config.get_console_fullname()

    url = "https://app.pendo.io/api/v1/track"
    headers = {
        'x-pendo-integration-key': "0ebad6d0-4351-478a-7412-c1d25365fd42",
        'content-type': "application/json"
    }
    body = {
        'name': user_fullname,
        'email': email,
        'type': 'track',
        'event': event_name,
        'visitorId': user_id,
        'accountId': account_id,
        'timestamp': timestamp,
        'context': {
            'ip': '192.168.0.1'
        },
        'properties': properties
    }
    res = requests.post(url, headers=headers, json=body)
    if (res.status_code != 200):
        print("Warning: could not talk to Pendo: {} {}".format(res.status_code, res.text),
              file=sys.stderr)
