import json
import logging

logger = logging.getLogger('main')


def get_token(session, instance, username, password):
    headers = {'Content-Type': 'application/json'}
    token_payload = {"username": username, "password": password, "grant_type": "password"}
    # get auth token and create headers dict
    response = session.post(instance + "/api/auth-service/token/", headers=headers, json=token_payload)
    logger.debug('Get token: %s', response.status_code)

    return json.loads(response.text)['access_token']