from ftw.upgrade import UpgradeStep


class ConfigureDefaultAspectRatios(UpgradeStep):
    """Configure default aspect ratios.
    """

    def __call__(self):
        self.install_upgrade_profile()
