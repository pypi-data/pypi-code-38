"""Migration from egov.contactdirectory to ftw.contacts.

The migration is not registered / executed automatically.
It must be executed manually from an upgrade step in an upgrade step of the
integration project.
"""

from ftw.upgrade import UpgradeStep
from ftw.upgrade.migration import InplaceMigrator


# Some sources will probably be removed after running the migration.
# But if the imports are kept and the sources are removed, the imports
# may raise ImportErrors. We only want to have those ImportErrors when
# we actually need to run the migration.
try:

    from ftw.upgrade.migration import DUBLIN_CORE_IGNORES

except ImportError, IMPORT_ERROR:
    pass
else:
    IMPORT_ERROR = None


class ExampleUpgradeStep(UpgradeStep):
    """This is just an example how an upgrade could be done in an upgrade
    step in the integration package.
    """

    def __call__(self):
        page_migrator = ContactMigrator()
        map(page_migrator.migrate_object,
            self.objects({'query': 'Contact'}), 'Migrate contacts')


class ContactMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(ContactMigrator, self).__init__(
            new_portal_type='ftw.contacts.Contact',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields + (
                    'description',  # invisible
                    'title',  # invisible
                    'effectiveDate',  # publication behavior not enabled
                    'expirationDate',  # publication behavior not enabled
                    'excludeFromNav',  # exclude from nav not enabled
                    'showPlacemark',  # field removed
                    'show_memberships',  # field removed
                    'subject',  # unused and field removed
                )),
            field_mapping={
                'tel_private': 'phone_private',
                'zip': 'postal_code',
                'zip_private': 'postal_code_private'},
            additional_steps=additional_steps,
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'Contact'}
        if path:
            query['path'] = path
        return query


class MemberMigrator(InplaceMigrator):
    """Requires the simplelayout profile to be installed.
    """

    def __init__(self, ignore_fields=(), additional_steps=(), options=0):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(MemberMigrator, self).__init__(
            new_portal_type='ftw.contacts.MemberBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields + (
                    'effectiveDate',  # unsuitable for blocks
                    'expirationDate',  # unsuitable for blocks
                    'excludeFromNav',  # unsuitable for blocks
                    'description',  # unnecessary
                    'subject',  # unnecessary
                )),
            field_mapping={
                'acquireAddress': 'acquire_address',
                'showTitle': 'show_title',
                'zip': 'postal_code'},
            additional_steps=additional_steps,
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'Member'}
        if path:
            query['path'] = path
        return query
