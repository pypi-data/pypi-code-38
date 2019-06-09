import base64
import json


class B64Utils:
    @staticmethod
    def file_from_base64(data, file_name):
        """
        Decodes base64 string from `data` and save it as binary file in `file_name`.
        """
        with open(file_name, "wb") as fh:
            fh.write(base64.b64decode(data))
        print("Saved to '{}'".format(file_name))


class JSONUtils:
    @staticmethod
    def pprint(origin_json):
        """
        It pretty prints the `origin_json` to show on the screen.
        """
        print(json.dumps(origin_json, indent=4, sort_keys=True))
