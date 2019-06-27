class AllowAll:
    def __call__(self, item):
        return item


class DenyAll:
    def __call__(self, item):
        raise TypeError("Deny all types")


# noinspection PyBroadException
class AnyMatch:
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, item):
        for validator in self.validators:
            try:
                return validator(item)
            except Exception:
                continue
        else:
            raise TypeError("No matches found")


class AllMatch:
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, item):
        for validator in self.validators:
            item = validator(item)

        return item
