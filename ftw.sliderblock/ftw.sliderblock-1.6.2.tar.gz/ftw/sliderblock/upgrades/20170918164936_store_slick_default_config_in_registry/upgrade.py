from ftw.upgrade import UpgradeStep


class StoreSlickDefaultConfigInRegistry(UpgradeStep):
    """Store Slick default config in registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
