import json
import requests

from bleach import config


def send(data):
    url = config.CONFIG['slackWebhook']

    # TODO check response for errors?
    response = requests.post(
        url=url,
        data=json.dumps({'text': data}),
        headers={'Content-Type': 'application/json'}
    )
