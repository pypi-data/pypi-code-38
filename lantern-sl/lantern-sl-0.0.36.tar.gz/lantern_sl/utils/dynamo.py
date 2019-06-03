import uuid

def unique_id():
    """ Generates a unique ID, for dynamo table's ids """
    return str(uuid.uuid4().hex)