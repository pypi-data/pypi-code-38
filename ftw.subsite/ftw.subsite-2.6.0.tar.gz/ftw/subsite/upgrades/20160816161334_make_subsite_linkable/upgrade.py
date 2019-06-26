from ftw.upgrade import UpgradeStep


class MakeSubsiteLinkable(UpgradeStep):
    """Make subsite linkable.
    """

    def __call__(self):
        self.install_upgrade_profile()
