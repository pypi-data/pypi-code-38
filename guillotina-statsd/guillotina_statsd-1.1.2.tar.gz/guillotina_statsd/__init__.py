from guillotina_statsd.middleware import middleware_factory  # noqa


app_settings = {
    "statsd": {
        "host": "localhost",
        "port": 8125,
        "key_prefix": "guillotina_request"
    },
    "load_utilities": {
        "statsd": {
            "provides": "guillotina_statsd.utility.IStatsdUtility",
            "factory": "guillotina_statsd.utility.StatsdUtility",
            "settings": {}
        }
    }
}


def includeme(root):
    """
    custom application initialization here
    """
    pass
