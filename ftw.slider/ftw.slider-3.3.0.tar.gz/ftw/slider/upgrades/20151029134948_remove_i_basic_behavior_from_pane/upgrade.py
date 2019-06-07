from ftw.upgrade import UpgradeStep


class RemoveIBasicBehaviorFromPane(UpgradeStep):
    """Remove i basic behavior from pane.
    """

    def __call__(self):
        self.install_upgrade_profile()
