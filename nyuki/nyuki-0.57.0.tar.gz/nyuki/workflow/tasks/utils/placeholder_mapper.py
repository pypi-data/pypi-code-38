def placeholder_mapper(data, default):

    class PlaceholderMapper(dict):
        def __missing__(self, key):
            return default

    return PlaceholderMapper(data)
