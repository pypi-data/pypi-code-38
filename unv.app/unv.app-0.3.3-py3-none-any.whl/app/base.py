import inspect
import asyncio

from .settings import SETTINGS


class Application:
    """Used for setup in other components to provide universal way
    of decomposing apps."""

    def __init__(self, setup: bool = True):
        self.registry = {type(self): self}
        self.run_tasks = []
        self.async_run_tasks = []
        self.setup_tasks = []

        if setup:
            self.setup()

    def register(self, app):
        type_ = type(app)
        if type_ in self.registry:
            raise ValueError(f'App type: "{type_}" already registered')
        self.registry[type_] = app

    def __getitem__(self, type_):
        return self.registry[type_]

    def __delitem__(self, type_):
        if type_ == type(self):
            raise ValueError(f'Do not unregister self-app: "{type_}"')
        self.registry.pop(type_)

    @property
    def components(self):
        return SETTINGS.get_components()

    def register_run_task(self, func):
        if inspect.iscoroutinefunction(func):
            self.async_run_tasks.append(func)
        else:
            self.run_tasks.append(func)

    def register_setup_task(self, func):
        self.setup_tasks.append(func)

    def _app_call(self, func):
        annotations = inspect.getfullargspec(func).annotations
        kwargs = {
            name: self.registry[type_]
            for name, type_ in annotations.items()
            if type_ in self.registry
        }
        return func(**kwargs)

    def setup(self):
        for component in self.components:
            self._app_call(component.setup)

        for task in self.setup_tasks:
            self._app_call(task)

    def run(self):
        for task in self.run_tasks:
            self._app_call(task)

        if not self.async_run_tasks:
            return

        async def async_tasks():
            await asyncio.gather(*[
                self._app_call(task) for task in self.async_run_tasks
            ], return_exceptions=True)

        asyncio.run(async_tasks())
