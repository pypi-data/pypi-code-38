from ftw.upgrade import UpgradeStep


class InstallPloneAppRelationfield(UpgradeStep):
    """Install plone.app.relationfield.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.ensure_installed('plone.app.relationfield:default')

    def ensure_installed(self, profile):
        portal_setup = self.getToolByName('portal_setup')
        version = portal_setup.getLastVersionForProfile(profile)
        if version not in (None, 'unknown'):
            return

        self.setup_install_profile(profile)
