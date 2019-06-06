import time
import uuid

from coolname import generate_slug


class Meta(object):
    """
        # Handle Metadata
        ---
        Handle metadata for the spaceman storage library. It should help us specify every detail according to what needs to be sent into a database.
    """

    def __init__(self):
        pass

    def store_meta(self, query, name="", generate_name=True, _is_current_time=True):
        """ Takes a query and settings to generate the dictionary """
        _timestamp = 0.0
        if self.check_required(query) == False:
            raise AttributeError("Missing either 'type' or 'timestamp'")

        if generate_name == False:
            if self.check_name(query) == False:
                raise AttributeError(
                    "If you choose not to generate a name, please ensure that it exist and is valid")
            file_name = f"{query['name']}.cereal"
            query['filename'] = file_name

        if generate_name:
            name = generate_slug()
            file_name = f"{name}.cereal"
            query['name'] = name
            query['filename'] = file_name

        if _is_current_time:
            query["timestamp"] = float(int(time.time()))

        return query

    def query_meta(self, query):
        if self.check_required(query) == False:
            raise AttributeError("Missing either 'type' or 'timestamp'")

        return query

    def check_name(self, query):
        if not isinstance(query, dict):
            raise TypeError("Query is not a dictionary")
        name = query.get("name")
        if name is None:
            return False

        is_valid = self.is_valid_name(name)
        if is_valid == False or name == "":
            raise NameError(
                "Name must be letters, numbers and '-' only. Nothing else is allowed")
        return True

    def check_required(self, query):
        # print(query)
        if isinstance(query, dict) == False:
            raise TypeError("Query is not a dictionary")
        _type = query.get("type", None)
        if _type is None:
            return False

        return True

    def is_valid_name(self, name):
        return all(c.isalnum() or c == '-' for c in name)
        # Check the format now
