import datetime
import logging

import pykube
import requests

from kopf.k8s import config

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1024
CUT_MESSAGE_INFIX = '...'


def post_event(*, obj, type, reason, message=''):
    """
    Issue an event for the object.
    """

    now = datetime.datetime.utcnow()

    # For cluster objects, post the events to the default namespace (there are no cluster events).
    namespace = obj.get('metadata', {}).get('namespace', 'default')

    # Prevent a common case of event posting errors but shortening the message.
    if len(message) > MAX_MESSAGE_LENGTH:
        infix = CUT_MESSAGE_INFIX
        prefix = message[:MAX_MESSAGE_LENGTH // 2 - (len(infix) // 2)]
        suffix = message[-MAX_MESSAGE_LENGTH // 2 + (len(infix) - len(infix) // 2):]
        message = f'{prefix}{infix}{suffix}'

    # Object reference - similar to the owner reference, but different.
    ref = dict(
        apiVersion=obj['apiVersion'],
        kind=obj['kind'],
        name=obj['metadata']['name'],
        uid=obj['metadata']['uid'],
        namespace=namespace,
    )

    body = {
        'metadata': {
            'namespace': namespace,
            'generateName': 'kopf-event-',
        },

        'action': 'Action?',
        'type': type,
        'reason': reason,
        'message': message,

        'reportingComponent': 'kopf',
        'reportingInstance': 'dev',
        'source' : {'component': 'kopf'},  # used in the "From" column in `kubectl describe`.

        'involvedObject': ref,

        'firstTimestamp': now.isoformat() + 'Z',  # '2019-01-28T18:25:03.000000Z' -- seen in `kubectl describe ...`
        'lastTimestamp': now.isoformat() + 'Z',  # '2019-01-28T18:25:03.000000Z' - seen in `kubectl get events`
        'eventTime': now.isoformat() + 'Z',  # '2019-01-28T18:25:03.000000Z'
    }

    try:
        api = config.get_pykube_api()
        obj = pykube.Event(api, body)
        obj.create()

    except requests.exceptions.HTTPError as e:
        # Events are helpful but auxiliary, they should not fail the handling cycle.
        # Yet we want to notice that something went wrong (in logs).
        logger.warning("Failed to post an event. Ignoring and continuing. "
                       f"Error: {e!r}. "
                       f"Event: type={type!r}, reason={reason!r}, message={message!r}.")
