class ExchangeRateObject:
    def __init__(self, result):
        self.base = result['base']
        self.rates = result['rates']
        self.date = None
        self.start_at = None
        self.end_at = None
        if "date" in result:
            self.date = result['date']
        if "end_at" in result:
            self.end_at = result['end_at']
        if "start_at" in result:
            self.start_at = result['start_at']

    def __str__(self):
        return '{} - {} - {} - {} - {}'.format(self.base, self.rates, self.date, self.start_at, self.end_at)


class PropellerObject:
    def __init__(self, res):
        self.result = res['result']
        self.meta = res['meta']

    def __str__(self):
        return '{} - {}'.format(self.result, self.meta)
        
        