from ftw.upgrade import UpgradeStep


class InstallContentTreeWidget(UpgradeStep):

    def __call__(self):
        profileid = 'plone.formwidget.contenttree:default'
        version = self.portal_setup.getLastVersionForProfile(profileid)
        if version == 'unknown':
            self.setup_install_profile('profile-' + profileid)
