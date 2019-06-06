import copy
import logging
import os
import sys

import ioc
import yaml

import qsa.const
from qsa.lib.pathfinder import Pathfinder


NOT_PROVIDED = object()


class QuantumSpecification:
    logger = logging.getLogger('qsa')
    codebase = ioc.class_property('core:CodeRepository')

    def __init__(self, config, assembler):
        self.observers = []
        self.spec = {}
        self.assembler = assembler
        self.config = config
        self.path = Pathfinder(config.getcwd())
        self.history_written = False

        assembler.observe(self)
        self.load()

    def exists(self):
        """Return a boolean indicating if a ``Quantumfile`` for the
        current project exists.
        """
        return self.codebase.exists('Quantumfile')

    def get(self, qualname, default=NOT_PROVIDED):
        """Get a configuration value by its qualified name."""
        keys = qualname.split('.')
        data = self.spec
        for i in range(0, len(keys)):
            key = keys[i]
            try:
                data = data[key]
            except KeyError:
                if default == NOT_PROVIDED:
                    raise
                data = default
                break
        return data

    def update(self, spec):
        """Updates the currrently loaded specification with dictionary
        `spec`.
        """
        self.spec.update(spec)

    def observe(self, observer):
        if observer in self.observers:
            raise Exception
        self.observers.append(observer)

    def notify(self, event, *args, **kwargs):
        """Notify all observers that `event` occurred."""
        for obs in self.observers:
            if not hasattr(obs, f'on_{event}'):
                continue
            getattr(obs, f'on_{event}')(*args, **kwargs)

    def init(self, typname, name, language=None, force=False, codebase=None):
        """Initializes a new Quantum specification."""
        if self.path.exists(qsa.const.QUANTUMFILE) and not force:
            raise NotImplementedError
        self.logger.debug("Initializing new %s",
            qsa.const.QUANTUMFILE)
        self.notify('project_init', self, typname, name, language=language)
        self.persist(codebase=codebase)

    def persist(self, codebase=None):
        """Persists the specification to the ``Quantumfile``."""
        dst = self.path.abspath(qsa.const.QUANTUMFILE)
        self.logger.info("Writing %s to %s", qsa.const.QUANTUMFILE, dst)
        self.codebase.write(dst, self.render(), mode='w')
        self.persist_history(self.codebase)
        return

        with open(dst, 'w') as f:
            f.write(self.render())
            self.persist_history()

    def persist_history(self, codebase=None):
        """Persists the command history of the QSA."""
        if self.history_written:
            return

        history = ''
        if codebase:
            if codebase.exists('.quantum_history'):
                history = open(codebase.abspath('.quantum_history')).read()
        else:
            if os.path.exists('.quantum_history'):
                history = open('.quantum_history').read()

        history = str.strip(history, '\n')\
            + '\n' + 'qsa ' + ' '.join(sys.argv[1:])
        if codebase:
            codebase.write('.quantum_history', history)
        else:
            with open('.quantum_history', 'w') as f:
                f.write(history)
        self.history_written = True

    def load(self):
        """Loads the ``Quantumfile`` and notifies all extensions."""
        if not self.path.exists(qsa.const.QUANTUMFILE):
            self.logger.warning("%s not found", qsa.const.QUANTUMFILE)
            data = {}
        else:
            with open(self.path.abspath(qsa.const.QUANTUMFILE)) as f:
                data = yaml.safe_load(f.read()) or {}
        self.notify('spec_loading', data, self)
        self.notify('spec_loaded', self)

    def render(self):
        """Renders the Quantumfile from its templates and return
        a string containing the result.
        """
        return Quantumfile.dump(self)

    def __iter__(self):
        return ((x, copy.deepcopy(y)) for x, y in self.spec.items())


class Quantumfile:

    @classmethod
    def dump(cls, spec):
        qf = cls(spec)
        return qf.sections

    @property
    def sections(self):
        return '\n\n\n'.join(x[0] for x in
            sorted(self._sections, key=lambda x: x[1]))

    def __init__(self, spec):
        self._spec = spec
        self._sections = []
        spec.notify('spec_render', self)

    def addsection(self, name, buf, weight=0):
        """Adds a section to the Quantumfile."""
        subsections = [buf.lstrip('-')]
        self._spec.notify('spec_section_render', self, name, subsections)
        self._sections.append(('\n\n'.join(subsections), weight))
