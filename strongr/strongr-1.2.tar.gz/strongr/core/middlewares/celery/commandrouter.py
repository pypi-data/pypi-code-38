from strongr.core.middlewares.celery.envelope import Envelope

class CommandRouter:
    _routes = {}
    _envelopes = {}
    _worker_envelopes = []

    def append_route(self, name_list, commandbus):
        for name in name_list:
            self._routes[name] = commandbus

    def handle_command(self, command):
        name = command.__module__.split('.')[1] + '.' + command.__class__.__name__.lower()
        if name in self._routes:
            return self._routes[name].handle(command)

    def bind_all_routes(self, celery_app):
        for route in self._routes.keys():
            self.enable_route_for_command(celery_app, route)

    def enable_worker_route_for_command(self, celery_app, name):
        if name not in self._envelopes:
            self.enable_route_for_command(celery_app, name)
            self._worker_envelopes.append(name)

    def enable_route_for_command(self, celery_app, name):
        """
        Register command with celery
        """
        if name not in self._envelopes:
            # envelope self-registers with Celery
            celery_app.conf.task_routes = self._generate_celery_routes(name) # update routes in celery
            self._envelopes[name] = Envelope()
            if '.query.' in name.lower():
                self._envelopes[name].patch(celery_app, name, False)
            else:
                self._envelopes[name].patch(celery_app, name, True)

    def _generate_celery_routes(self, append):
        out = {}
        for route in self._routes.keys():
            out[route] = {'queue': route}

        if append not in out:
            out[append] = {'queue': append}

        return out

    def get_remotable_command_for(self, name):
        return self._envelopes[name]

    def has_remotable_command_registered(self, name):
        return name in self._envelopes and name not in self._worker_envelopes
