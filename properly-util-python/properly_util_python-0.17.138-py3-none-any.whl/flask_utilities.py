from properly_util_python.dynamo_helper import EnvironmentControlledDynamoHelper


class ViewConfig:
    """
    The ViewConfig is a convenience wrapper class that contains all the information necessary for
    Flask to fully define a REST endpoint.
    """
    def __init__(self, klass: type, name: str, rule: str, methods: list):
        """
        The Flask REST endpoint wrapper class.
        :param klass: The Flask view class.
        :param name: The ID name of the Flask REST endpoint.
        :param rule: The REST endpoint path rule.
        :param methods: The supported ways to access the Flask REST endpoint.
        """
        self.klass = klass
        self.name = name
        self.rule = rule
        self.methods = methods


def add_flask_views(app, view_configs: list):
    """
    The helper method that initializes and adds the Flask REST endpoints defined in the
    ViewConfigs to the Flask app instance.
    :param app: The Flask app instance.
    :param view_configs: The list of ViewConfigs to define REST endpoints.
    """
    for view_config in view_configs:
        view = view_config.klass.as_view(
            name=view_config.name,
            app=app,
            dynamo_helper=EnvironmentControlledDynamoHelper()
        )
        app.add_url_rule(
            rule=view_config.rule,
            view_func=view,
            methods=view_config.methods
        )
