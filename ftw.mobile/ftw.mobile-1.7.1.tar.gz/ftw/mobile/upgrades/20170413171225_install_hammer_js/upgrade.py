from ftw.upgrade import UpgradeStep


class InstallHammerJS(UpgradeStep):
    """Install hammer js.
    """

    def __call__(self):
        self.install_upgrade_profile()
