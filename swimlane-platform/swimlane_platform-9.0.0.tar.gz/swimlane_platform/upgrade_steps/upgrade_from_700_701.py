from semver import VersionInfo

from swimlane_platform.lib import info_function_start_finish
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver


class UpgradeFrom700To701(UpgradeStep):
    FROM = semver.parse_version_info('7.0.0')  # type: VersionInfo
    TO = semver.parse_version_info('7.0.1')  # type: VersionInfo

    @info_function_start_finish('Upgrade From 7.0.0 To 7.0.1')
    def process(self):
        # type: () -> None
        pass
