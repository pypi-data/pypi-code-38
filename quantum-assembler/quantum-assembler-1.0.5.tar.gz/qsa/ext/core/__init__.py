import ioc

from qsa.lib.repository import CodeRepository
from qsa.ext.base import BaseExtension


class Extension(BaseExtension):
    name = 'core'

    def setup_injector(self, injector):
        self.provide_class(CodeRepository(self.config.workdir))
