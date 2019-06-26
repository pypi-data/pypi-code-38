from properly_util_python.dynamo_helper import EnvironmentControlledDynamoHelper


class ViewConfig:
    def __init__(self, klass: type, name: str, rule: str, methods: list):
        """
        A wrapper of all the information needed to construct and add a Flask view
        :param klass: The class instance of the Flask view
        :param name: The name of the Flask endpoint
        :param rule: The REST path of the Flask endpoint
        :param methods: The REST methods allowed
        """
        self.klass = klass
        self.name = name
        self.rule = rule
        self.methods = methods


class FlaskHelper:
    @staticmethod
    def add_view_configs(app, view_configs: list[ViewConfig]):
        """
        Initializes Flask views based on the provided list of `ViewConfig`

        :param app: The Flask application
        :param view_configs: The list of `ViewConfig` objects
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
