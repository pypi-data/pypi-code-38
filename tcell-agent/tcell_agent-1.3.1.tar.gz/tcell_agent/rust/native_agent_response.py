import json


def convert_bytes_string_to_json_object(native_method_name, response, response_len):
    try:
        return json.loads(
            "".join([chr(response_byte) for response_byte in response[:response_len]])
        )
    except ValueError:
        return {
            "errors": [
                "Could not decode json response from `{}` in native library.".format(native_method_name)
            ]
        }


class NativeAgentResponse(object):
    def __init__(self, native_method_name, response, response_len):
        self.response = {}
        self.errors = []

        if response_len < 0:
            self.errors.append(
                "Error response from `{}` in native library method: {}".format(native_method_name,
                                                                               response_len)
            )
        else:
            self.response = convert_bytes_string_to_json_object(native_method_name, response, response_len)
            if self.response.get("errors"):
                for error in self.response["errors"]:
                    self.errors.append(
                        "{} {} {}".format(native_method_name, "returned an error:", error)
                    )
                self.response = {}
            if self.response.get("error"):
                self.errors.append(
                    "{} {} {}".format(native_method_name, "returned an error:", self.response["error"])
                )
                self.response = {}

    def get_errors(self):
        return self.errors

    def get_response_without_errors(self):
        return self.response


class EmptyNativeAgentResponse(NativeAgentResponse):
    def __init__(self):  # pylint: disable=super-init-not-called
        self.response = {}
        self.errors = []
