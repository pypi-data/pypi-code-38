from abc import ABCMeta


class IIdentifier:
    __metaclass__ = ABCMeta

    def __init__(self, name: str):
        self.name = name


class AppIdentifier(IIdentifier):
    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self) -> str:
        return 'app name: {}'.format(self.name)


class AppInstanceIdentifier(IIdentifier):
    def __init__(self, name: str, infra_id: str):
        super().__init__(name)
        self.name = name
        self.infra_id = infra_id

    def __eq__(self, other):
        if type(other) == type(self):
            return self._is_equal_to_me(other)
        return NotImplemented

    def _is_equal_to_me(self, other):
        return other.name == self.name and other.infra_id == self.infra_id

    def __hash__(self):
        return hash((self.name, self.infra_id))

    def __str__(self) -> str:
        return 'app name: {APP_NAME}, infra id: {INFRA_ID}'.format(APP_NAME=self.name, INFRA_ID=self.infra_id)
