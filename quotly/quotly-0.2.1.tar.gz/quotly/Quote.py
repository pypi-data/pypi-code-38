class Quote:
    def __init__(self, *values):
        self.quote = None
        self.targets = []

        if values is not None and values[0] is not None:
            self.quote = values[0][0]

            for t in values[0][1:]:
                if t is not None and len(t) > 0:
                    self.targets.append(t)

    @staticmethod
    def from_tuple(quote, *targets):
        return Quote((quote, targets))

    def __str__(self):
        if self.quote is not None:
            return '"{0}" -{1}'.format(self.quote, self.targets[0] if len(self.targets) > 0 else 'Unknown')

        return 'Sorry! Found no suitable quote for your input.'
