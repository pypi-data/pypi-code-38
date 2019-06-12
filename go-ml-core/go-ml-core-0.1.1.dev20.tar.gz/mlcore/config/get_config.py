import yaml

def get_config(ymlfile):
    stream = open(ymlfile, 'r')
    docs = list(yaml.load_all(stream))

    #print('config = %s' % docs[0])
    return docs[0]