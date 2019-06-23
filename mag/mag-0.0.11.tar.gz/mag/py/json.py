import json
def load_to_local(file:str) -> dict:
    '''
    Reads the passed file and dumps all keys into locals()

    Args:
        file (str): fullpath to a simple key: value json file

    Returns:
        data (dict): the contents of the json file
    '''
    with open(file, 'r') as f:
        data = json.load(f)
        for var, val in data.items():
            locals()[var] = val
        return data
