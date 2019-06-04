from ftw.upgrade import UpgradeStep


class MoveToResourcesDirectory(UpgradeStep):
    """Move to resources directory.
    """

    def __call__(self):
        self.install_upgrade_profile()
