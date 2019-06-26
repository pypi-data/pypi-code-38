from ftw.upgrade import UpgradeStep


class UpdateCSSRegistry(UpgradeStep):
    """Update css registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
