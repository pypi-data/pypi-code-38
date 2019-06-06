import yaml

def get_config(ymlfile):
    with open(ymlfile, 'r') as stream:
        docs = list(yaml.load_all(stream))

    #print('config = %s' % docs[0])
    return docs[0]
