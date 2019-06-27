class Quote:
    def __init__(self, quote, *targets):
        self.quote = quote
        self.targets = []

        for t in targets:
            self.targets.append(t[0])

    def has_target(self, target):
        return target in self.targets

    @staticmethod
    def filter_by_target(seq, target):
        for elem in seq:
            if target in elem.targets:
                yield elem

    @staticmethod
    def filter_by_targets(seq, targets):
        for elem in seq:
            if targets in elem.targets:
                yield elem
