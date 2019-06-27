from ftw.upgrade import UpgradeStep


class AddImageCroppingBehaviorToPane(UpgradeStep):
    """Add image cropping behavior to pane.
    """

    def __call__(self):
        self.install_upgrade_profile()
