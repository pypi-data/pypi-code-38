from swimlane_platform.lib import BaseWithLog
from abc import abstractproperty, ABCMeta, abstractmethod
import semver


class UpgradeStep(BaseWithLog):
    __metaclass__ = ABCMeta

    @abstractproperty
    def FROM(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractproperty
    def TO(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractmethod
    def process(self):
        # type: () -> None
        pass
