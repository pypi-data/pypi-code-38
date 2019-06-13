import logging
from requests import exceptions


from urllib.parse import urlparse

import deriva.core.ermrest_model as em
from deriva.core.ermrest_config import tag as chaise_tags

from deriva.utils.catalog.components.deriva_model import DerivaCatalog, DerivaSchema, DerivaColumn, \
    DerivaTable, DerivaContext, DerivaKey, DerivaForeignKey, DerivaCatalogError, DerivaModel

logger = logging.getLogger(__name__)

chaise_tags.catalog_config = 'tag:isrd.isi.edu,2019:catalog-config'


class DerivaConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg


class DerivaCatalogConfigure(DerivaCatalog):
    """
    DerovaCatalogConfigure extends DerivaCatalog by providing methods for creating a default configuration for a
    catalog.

    The only method of interest in this class is configure_baseline_catalog.

    """
    def __init__(self, host, scheme='https', catalog_id=1):
        super().__init__(host, scheme=scheme, catalog_id=catalog_id)

    def _make_schema_instance(self, schema_name):
        return DerivaSchemaConfigure(self, schema_name)

    def _configure_ermrest_client(self, groups):
        """
        Set up ermrest_client table so that it has readable names and uses the display name of the user as the row name.
        :param groups:
        :return:
        """

        ermrest_client = self.catalog['public']['ERMrest_Client']

        # Make ermrest_client table visible.  If the GUID or member name is considered sensitivie, then this needs to be
        # changed.
        ermrest_client.acls['select'] = ['*']

        # Set table and row name.
        ermrest_client.annotations.update({
            chaise_tags.display: {'name': 'Users'},
            chaise_tags.visible_columns: {'compact': ['ID', 'Full_Name', 'Display_Name', 'Email']},
            chaise_tags.table_display: {'row_name': {'row_markdown_pattern': '{{{Full_Name}}}'}}
        })

        column_annotations = {
            'RCT': {chaise_tags.display: {'name': 'Creation Time'}},
            'RMT': {chaise_tags.display: {'name': 'Modified Time'}},
            'RCB': {chaise_tags.display: {'name': 'Created By'}},
            'RMB': {chaise_tags.display: {'name': 'Modified By'}}
        }
        for k, v in column_annotations.items():
            ermrest_client.column(k).annotations.update(v)
        return

    def _configure_www_schema(self):
        """
        Set up a new schema and tables to hold web-page like content.  The tables include a page table, and a asset
        table that can have images that are referred to by the web page.  Pages are written using markdown.
        :return:
        """
        self.logger.info('Configuring WWW schema')
        # Create a WWW schema if one doesn't already exist.
        try:
            www_schema = self.create_schema('WWW', comment='Schema for tables that will be displayed as web content')
        except DerivaCatalogError as e:
            if 'already exists' not in e.args[0]:
                raise
            else:
                www_schema = self['WWW']

        # Create the page table
        try:
            www_schema.create_table(
                'Page',
                column_defs=[
                    DerivaColumn.define('Title', 'text', nullok=False, comment='Unique title for the page'),
                    DerivaColumn.define('Content', 'markdown', comment='Content of the page in markdown')
                ],
                key_defs=[DerivaKey.define(['Title'])],
                annotations={
                    chaise_tags.table_display: {'detailed': {'hide_column_headers': True, 'collapse_toc_panel': True}
                                                },
                    chaise_tags.visible_foreign_keys: {'detailed': {}},
                    chaise_tags.visible_columns: {'detailed': ['Content']}}

            )
        except DerivaCatalogError as e:
            if 'already exists' not in e.args[0]:
                raise
        table = DerivaTableConfigure(self, 'WWW', 'Page')
        table.configure_table_defaults()

        # Now set up the asset table
        try:
            table.create_asset_table('RID')
        except ValueError as e:
            if 'already exists' not in e.args[0]:
                raise

        return self

    def _set_core_groups(self, catalog_name=None, admin=None, curator=None, writer=None, reader=None,
                         replace=False):
        """
        Look in the catalog to get the group IDs for the four core groups used in the baseline configuration. There are
        three options:  1) core group name can be provided explicitly, 2) group name can be formed from a catalog
        name and a default group name, 3) group name can be formed from the host name and a default group name.
        :param catalog_name: Name of the catalog to use as a prefix in looking up default name of the group. Default
               group names are formed by combining the catalog_name with the standard group name: e.g. foo-admin
               foo-writer, and foo-reader
        :param admin: Group name to use in place of default
        :param curator: Group name to use in place of default
        :param writer: Group name to use in lace of default
        :param reader: Either '*' for anonymous read access, or the group name to use in place of default
        :param replace: Ignore existing catalog config and use provided arguements.
        :return: dictionary with the four group ids.
        """
        groups = {}
        # Get previous catalog configuration values if they exist
        if chaise_tags.catalog_config in self.annotations and not replace:
            groups.update({
                'admin': self.annotations[chaise_tags.catalog_config]['groups']['admin'],
                'curator': self.annotations[chaise_tags.catalog_config]['groups']['curator'],
                'writer': self.annotations[chaise_tags.catalog_config]['groups']['writer'],
                'reader': self.annotations[chaise_tags.catalog_config]['groups']['reader']
            })
        else:
            if admin == '*' or curator == '*' or writer == '*':
                raise DerivaConfigError(msg='Only reader may be anonymous when setting core catalog groups')
            if not catalog_name and (admin is None or curator is None or writer is None or reader is None):
                raise DerivaConfigError(msg='Catalog name required to look up group')

            if admin is None:
                admin = catalog_name + '-admin'
            if curator is None:
                curator = catalog_name + '-curator'
            if writer is None:
                writer = catalog_name + '-writer'
            if reader is None:
                reader = catalog_name + '-reader'

            pb = self.getPathBuilder()
            catalog_groups = {i['Display_Name']: i for i in pb.public.ERMrest_Group.entities()}
            groups = {}
            try:
                groups.update({
                    'admin': catalog_groups[admin]['ID'],
                    'curator': catalog_groups[curator]['ID'],
                    'writer': catalog_groups[writer]['ID'],
                    'reader': catalog_groups[reader]['ID'] if reader is not '*' else '*'
                })
            except KeyError as e:
                raise DerivaConfigError(msg='Group {} not defined'.format(e.args[0]))

        return groups

    def _configure_group_table(self, groups):
        """
        Create a table in the public schema for tracking mapping of group names.
        :param groups:
        :return:
        """

        logging.info('Configuring groups')
        ermrest_group = self['public']['ERMrest_Group']

        # Make ERMrest_Group table visible to writers, curators, and admins.
        ermrest_group.acls['select'] = [groups['writer'], groups['curator'], groups['admin']]

        # Set table and row name.
        ermrest_group.annotations.update({
            chaise_tags.display: {'name': 'Globus Group'},
            chaise_tags.visible_columns: {'*': ['Display_Name', 'Description', 'URL', 'ID']},
            chaise_tags.table_display: {'row_name': {'row_markdown_pattern': '{{{Display_Name}}}'}}
        })

        # Set compound key so that we can link up with Visible_Group table.
        try:
            ermrest_group.create_key(['ID', 'URL', 'Display_Name', 'Description'], comment='Group ID is unique.')
        except exceptions.HTTPError as e:
            if 'already exists' not in e.args[0]:
                raise

        # Create a catalog groups table
        column_defs = [
            DerivaColumn.define('Display_Name', em.builtin_types['text']),
            DerivaColumn.define('URL', em.builtin_types['text'],
                                annotations={
                                    chaise_tags.column_display: {
                                        '*': {'markdown_pattern': '[**{{Display_Name}}**]({{{URL}}})'}},
                                    chaise_tags.display: {'name': 'Group Management Page'}
                                }
                                ),
            DerivaColumn.define('Description', em.builtin_types['text']),
            DerivaColumn.define('ID', em.builtin_types['text'], nullok=False)
        ]

        key_defs = [
            DerivaKey.define(['ID']),
            DerivaKey.define(['ID', 'URL', 'Display_Name', 'Description'],
                             comment='Key to ensure that group only is entered once.'
                             ),
        ]

        # Set up a foreign key to the group table so that the creator of a record can only select
        # groups of which they are members of for values of the Owners column.
        fkey_group_policy = {
            # FKey to group can be created only if you are a member of the group you are referencing
            'set_owner': {"types": ["insert"],
                          "projection": ["ID"],
                          "projection_type": "acl"}
        }

        # Allow curators to also update the foreign key.
        fkey_group_acls = {"insert": [groups['curator']], "update": [groups['curator']]}

        # Create a foreign key to the group table. Set update policy to keep group entry in sync.
        fkey_defs = [
            DerivaForeignKey.define(['ID', 'URL', 'Display_Name', 'Description'],
                                    ermrest_group, ['ID', 'URL', 'Display_Name', 'Description'],
                                    on_update='CASCADE',
                                    acls=fkey_group_acls,
                                    acl_bindings=fkey_group_policy,
                                    )
        ]

        # Create the visible groups table. Set ACLs so that writers or curators can add entries or edit.  Allow writers
        # to be able to create new entries.  No one is allowed to update, as this is only done via the CASCADE.
        # Get or create Catalog_Group table....
        try:
            self['public'].create_table(
                'Catalog_Group', column_defs=column_defs,
                key_defs=key_defs, fkey_defs=fkey_defs,
                comment=None,
                acls={
                    # Make ERMrest_Group table visible to members of the group members, curators, and admins.
                    'select': [groups['reader']],
                    'insert': [groups['writer'],
                               groups['curator']]
                },
                acl_bindings={},
                annotations={
                    chaise_tags.table_display: {
                        'row_name': {'row_markdown_pattern': '{{{Display_Name}}}'}}},
            )
        except ValueError as e:
            if 'already exists' not in e.args[0]:
                raise
        table = DerivaTableConfigure(self, 'public', 'Catalog_Group')
        table.configure_table_defaults(set_policy=False)
        return

    def configure_baseline_catalog(self,
                                   catalog_name=None,
                                   admin=None, curator=None, writer=None, reader=None,
                                   set_policy=True,
                                   public=False):
        """
        Put catalog into standard configuration which includes:

        1. Setting default display mode to be to turn underscores to spaces.
        2. Set access control assuming admin, curator, writer, and reader groups.
        3. Configure ermrest_client to have readable names.
        4. Create a schema called *WWW* and create a *Page* table in that schema configured to display web-page like
        content.

        :param catalog_name: Name to use when looking up catalog groups.  Defaults to host name if not provided.
        :param admin: Name of the admin group.  Defaults to catalog-admin, where catalog is the catalog_name
        :param curator: Name of the curator group. Defaults to catalog-curator
        :param writer: Name of the writer group. Defaults to catalog-writer
        :param reader: Name of the reader group. Defaults to catalog-reader
        :param set_policy: Set policy for catalog to support reader/writer/curator/admin groups.
        :param public: Set to true if anonymous read access should be allowed.
        """
        with DerivaModel(self.catalog):
            if not catalog_name:
                # If catalog name is not provided, default to the host name of the host.
                catalog_name = urlparse(self.ermrest_catalog.get_server_uri()).hostname.split('.')[0]
            groups = self._set_core_groups(catalog_name=catalog_name,
                                           admin=admin, curator=curator, writer=writer, reader=reader)

            # Record configuration of catalog so we can retrieve when we configure tables later on.
            self.annotations[chaise_tags.catalog_config] = {'name': catalog_name, 'groups': groups}

            # Set up default name style for all schemas.
            for s in self.schemas:
                s.annotations[chaise_tags.display] = {'name_style': {'underline_space': True}}

            # modify catalog ACL config to support basic admin/curator/writer/reader access.
            if set_policy:
                self.acls.update({
                    "owner": [groups['admin']],
                    "insert": [groups['curator'], groups['writer']],
                    "update": [groups['curator']],
                    "delete": [groups['curator']],
                    "select": [groups['writer'], groups['reader']] if not public else ['*'],
                    "enumerate": ["*"],
                })

            self._configure_ermrest_client(groups)
            self._configure_group_table(groups)
            self._configure_www_schema()


def update_group_table(catalog):
    def group_urls(group):
        guid = group.split('/')[-1]
        link = 'https://app.globus.org/groups/' + guid
        uri = 'https://auth.globus.org/' + guid
        return link, uri

    pb = catalog.getPathBuilder()
    # Attempt to add URL.  This can go away once we have URL entered by ERMrest.
    pb.public.ERMrest_Group.update(
        [{'RID': i['RID'], 'URL': group_urls(i['ID'])[0]} for i in pb.public.ERMrest_Group.entities()]
    )


class DerivaSchemaConfigure(DerivaSchema):
    """
    This is a shim class that is used to make sure that a DerivaCatalogConfigure returns a DerivaTableConfigure
    """
    def __init__(self, catalog, schema_name):
        super(DerivaSchemaConfigure, self).__init__(catalog, schema_name)

    def _make_table_instance(self, schema_name, table_name):
        return DerivaTableConfigure(self.catalog, schema_name, table_name)


class DerivaTableConfigure(DerivaTable):
    """
    This class is used to create a default configuration for a Deriva Table.
    """
    def __init__(self, catalog, schema_name, table_name):
        super(DerivaTableConfigure, self).__init__(catalog, schema_name, table_name)
        return

    def configure_self_serve_policy(self, groups):
        """
        Set up a table so it has a self service policy.  Add an owner column if one is not present, and set the acl
        binding so that it follows the self service policy.

        :param groups: dictionary of core catalog groups
        :return:
        """

        # Configure table so that access can be assigned to a group.  This requires that we create a column and
        # establish a foreign key to an entry in the group table.  We will set the access control on the foreign key
        # so that you are only able to delagate access to a the creator of the entity belongs to.
        if 'Owner' not in self.columns:
            self.create_columns(DerivaColumn.define('Owner', 'text', comment='Group that can update the record.'))

        # Now configure the policy on the table...
        self_service_policy = {
            # Set up a policy for the table that allows the creator of the record to update and delete the record.
            "self_service_creator": {
                "types": ["update", 'delete'],
                "projection": ["RCB"],
                "projection_type": "acl"
            },
            # Set up a policy for the table that allows members of the group referenced by the Owner column to
            # update and delete the record.
            'self_service_group': {
                "types": ["update", "delete"],
                "projection": ["Owner"],
                "projection_type": "acl"
            }
        }

        # Make table policy be self service, creators and owners can update.
        self.acl_bindings.update(self_service_policy)

        # Set up a foreign key to the group table on the owners column so that the creator of a record can only
        # select groups of which they are members of for values of the Owners column.
        fkey_group_policy = {
            # FKey to group can be created only if you are a member of the group you are referencing
            'set_owner': {"types": ["update", "insert"],
                          "projection": ["ID"],
                          "projection_type": "acl"}
        }

        # Allow curators to also update the foreign key.
        fkey_group_acls = {"insert": [groups['curator']], "update": [groups['curator']]}

        # Delete old fkey if there is one laying around....
        for fk in self.foreign_keys:
            if len(fk.columns) == 1 and next(iter(fk.columns)).name == 'Owner':
                fk.delete()

        # Now create the foreign key to the group table.
        self.create_foreign_key(['Owner'],
                                self.catalog['public']['Catalog_Group'], ['ID'],
                                acls=fkey_group_acls, acl_bindings=fkey_group_policy,

                                )
        return

    def create_default_visible_columns(self, really=False):

        column_sources, outbound_sources, inbound_sources = self.sources(merge_outbound=True)
        location = {'RCB': ['Owner']} if 'Owner' in self.columns else {}

        # Don't overwrite existing annotations if they are already in place.
        if chaise_tags.visible_columns not in self.annotations:
            self.annotations[chaise_tags.visible_columns] = {}
        positions = {}
        if '*' not in self.annotations[chaise_tags.visible_columns] or really:
            positions.update({DerivaContext('*'): location})
            self.visible_columns.insert_context(DerivaContext('*'), column_sources)
        if 'entry' not in self.annotations[chaise_tags.visible_columns] or really:
            positions.update({DerivaContext('entry'): location})
            self.visible_columns.insert_context(DerivaContext('entry'), column_sources)

        self.visible_columns.reorder_visible_source(positions)

    def create_default_visible_foreign_keys(self, really=False):
        _, _, inbound_sources = self.sources()
        self.logger.debug('visible_fkeys {}'.format(inbound_sources))
        # Don't overwrite existing annotations if they are already in place.
        if chaise_tags.visible_foreign_keys not in self.annotations:
            self.annotations[chaise_tags.visible_foreign_keys] = {}
        if '*' not in self.annotations[chaise_tags.visible_foreign_keys] or really:
            self.visible_foreign_keys.insert_context(DerivaContext('*'), inbound_sources)

    def configure_table_defaults(self, set_policy=True, public=False, reset_visible_columns=True):
        """
        This function adds the following basic configuration details to an existing table:

        1. Creates a self service modification policy in which creators can update update any row they create.
           Optionally, an Owner column can be provided, which allows the creater of a row to delegate row ownership to
           a specific group.
        2. Adds display annotations and foreign key declarations so that system columns RCB, RMB display in a user
           friendly way.
        3. Adds a visible_foreign_keys and visible_columns annotation.

        :param set_policy: If true, then configure the table to have a self service policy
        :param public: Make table acessible without logging in.
        :param reset_visible_columns: Overwrite any existing visible_columns annotation.
        """

        if chaise_tags.catalog_config not in self.catalog.annotations:
            raise DerivaConfigError(msg='Attempting to configure table before catalog is configured')

        # Hack to update description and URL until we get these passed through ermrest....
        update_group_table(self.catalog)

        if public:
            # First copy over any inherited ACLS.
            self.acls.update({**self.schema.acls, **self.acls})
            self.acls.pop("create", None)
            # Now add permision for anyone to read.
            self.acls['select'] = ['*']

        if set_policy:
            self.configure_self_serve_policy(self.catalog.get_groups())

        # Configure schema if not already done so.
        if chaise_tags.display not in self.schema.annotations:
            self.schema.annotations[chaise_tags.display] = {}
        if 'name_style' not in self.schema.annotations[chaise_tags.display]:
            self.schema.annotations[chaise_tags.display].update({'name_style': {'underline_space': True}})

        # Set up foreign key to ermrest_client on RCB, RMB and Owner. If ermrest_client is configured, the
        # full name of the user will be used for the FK value.
        for col, display in [('RCB', 'Created By'), ('RMB', 'Modified By')]:
            # Delete old fkey if there is one laying around....
            for fk in self.foreign_keys:
                if len(fk.columns) == 1 and next(iter(fk.columns)).name == col:
                    fk.delete()

            self.create_foreign_key([col], self.catalog['public']['ERMrest_Client'], ['ID'])
            # Add a display annotation so that we have sensible name for RCB and RMB.
            self.columns[col].annotations[chaise_tags.display] = {'name': display}

        self.columns['RCT'].annotations.update({chaise_tags.display: {'name': 'Creation Time'}})
        self.columns['RMT'].annotations.update({chaise_tags.display: {'name': 'Modified Time'}})

        self.create_default_visible_columns(really=reset_visible_columns)
