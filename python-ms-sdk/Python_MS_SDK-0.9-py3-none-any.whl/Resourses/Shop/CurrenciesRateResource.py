from ms_sdk.Resourses import Resource


class CurrenciesRateResource(Resource):
    """
    Class CurrenciesRateResource
    :method CurrencyRate get(int id):
    :method CurrencyRate first():
    :method CurrencyRate[] all():
    :method CurrencyRate update(id, data):
    :method CurrencyRate create(data):
    """

    def getURI(self):
        return 'currenciesrate'