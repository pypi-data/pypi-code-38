from ms_sdk.Resourses import Resource


class CurrenciesResource(Resource):
    """
    Class CurrenciesResource
    :method Currency get(int id):
    :method Currency first():
    :method Currency[] all():
    :method Currency update(id, data):
    :method Currency create(data):
    """

    def getURI(self):
        return 'currencies'