from ftw.upgrade import UpgradeStep
from ftw.upgrade.migration import BACKUP_AND_IGNORE_UNMAPPED_FIELDS
from ftw.upgrade.migration import InplaceMigrator


class MigrateToDexterity(UpgradeStep):
    """Migrate to dexterity.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.simplelayout.contenttypes:default')
        self.install_upgrade_profile()

        migrator = InplaceMigrator(
            new_portal_type='ftw.subsite.Subsite',
            options=BACKUP_AND_IGNORE_UNMAPPED_FIELDS,
            field_mapping={
                'FromEmail': 'from_email',
                'FromName': 'from_name',
                'forcelanguage': 'force_language',
                'linkSiteInLanguagechooser': 'link_site_in_languagechooser',
            }
        )

        map(migrator.migrate_object,
            self.objects({'portal_type': 'Subsite'}, 'Migrate to dexterity.'))
