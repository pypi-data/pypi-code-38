import importlib
import logging
import pkgutil
import os


class Assembler:
    logger = logging.getLogger('qsa')

    def __init__(self, config, injector):
        self.config = config
        self.injector = injector
        self.observers = []
        self.extensions = self.find_extensions()

    def fullassemble(self):
        """Assemble, render and compile all configured QSA extensions
        for the current project.
        """
        for ext in self.extensions:
            self.logger.info("Updating %s", ext.name)
            self.injector.call(ext.handle)

    def notify(self, event, *args, **kwargs):
        """Notify all observers that `event` occurred."""
        for obs in self.observers:
            if not hasattr(obs, f'on_{event}'):
                continue
            if not self.injector.call(obs.can_handle):
                self.logger.debug("Skipping event %s for extension '%s'",
                    event, obs.name)
                continue
            getattr(obs, f'on_{event}')(*args, **kwargs)

    def observe(self, observable):
        for ext in self.extensions:
            observable.observe(ext)
        return observable

    def find_extensions(self):
        """Find all extensions in the qsa.ext package."""
        dirname = os.path.join(os.path.dirname(__file__), 'ext')
        extensions = []
        for loader, name, ispkg in pkgutil.iter_modules([dirname]):
            if name == 'base':
                continue
            module_name = "qsa.ext.%s" % name
            module = importlib.import_module(module_name)
            extensions.append(module.Extension(self.config, self, self.injector))
            self.observers.append(extensions[-1])

        # Allow extensions to setup the injector.
        for ext in extensions:
            ext.setup_injector(self.injector)

        # Set up the command-line interface.
        for ext in extensions:
            self.injector.call(ext._createcommand)
        self.notify('extensions_loaded', extensions)

        # Allow extensions to setup the injector.
        for ext in extensions:
            self.injector.call(ext.setup)

        return extensions
