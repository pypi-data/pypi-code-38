from ftw.upgrade import UpgradeStep


class AddLDAPRegistry(UpgradeStep):
    """Add ldap registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
