from ftw.upgrade import UpgradeStep


class AddMemberRegistryForSourcePath(UpgradeStep):
    """Add member registry for source path.
    """

    def __call__(self):
        self.install_upgrade_profile()
