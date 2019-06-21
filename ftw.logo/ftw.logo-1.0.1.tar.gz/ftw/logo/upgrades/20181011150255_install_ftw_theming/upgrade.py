from ftw.upgrade import UpgradeStep


class InstallFtwTheming(UpgradeStep):
    """install ftw.theming.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.ensure_profile_installed('profile-ftw.theming:default')
