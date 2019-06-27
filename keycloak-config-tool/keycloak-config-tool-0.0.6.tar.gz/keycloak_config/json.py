import json


class JsonLoader():
    """
    A wrapper class for the json library, doing transparent string value decryption.
    """

    def __init__(self, encryption_helper):
        self.encryption_helper = encryption_helper

    def load_json(self, json_content):
        content = json.loads(json_content)
        return self.encryption_helper.decrypt(content)
