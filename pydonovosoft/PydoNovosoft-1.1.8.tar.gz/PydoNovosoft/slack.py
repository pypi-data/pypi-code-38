import json
import requests


class Slack(object):

    def __init__(self, hook=""):
        self._hook = hook

    def post(self, channel, message):
        post = {"text": "{0}".format(message["text"]), "username": message["user"], "channel": channel}
        json_data = json.dumps(post)
        resp = requests.post(self._hook, data=json_data.encode('ascii'), headers={'Content-Type': 'application/json'})
        return resp

    def post_attachments(self, channel, message, attachments):
        post = {"username": message["user"], "channel": channel, "attachments": attachments}
        json_data = json.dumps(post)
        resp = requests.post(self._hook, data=json_data.encode('ascii'), headers={'Content-Type': 'application/json'})
        return resp
