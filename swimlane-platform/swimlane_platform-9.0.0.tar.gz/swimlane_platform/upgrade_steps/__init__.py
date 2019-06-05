from typing import List, Type
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from swimlane_platform.upgrade_steps.upgrade_from_700_701 import UpgradeFrom700To701
from swimlane_platform.upgrade_steps.upgrade_from_701_800 import UpgradeFrom701To800
from swimlane_platform.upgrade_steps.upgrade_from_800_801 import UpgradeFrom800To801
from swimlane_platform.upgrade_steps.upgrade_from_801_900 import UpgradeFrom801To900

Upgrades = [UpgradeFrom700To701, UpgradeFrom701To800, UpgradeFrom800To801, UpgradeFrom801To900]  # type: List[Type[UpgradeStep]]
