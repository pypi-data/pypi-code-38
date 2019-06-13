import logging
import os
import os.path


from deriva.core import get_credential, init_logging, DerivaServer
from deriva.utils.catalog.components.deriva_model import DerivaColumn, DerivaModel
from deriva.utils.catalog.components.configure_catalog import DerivaCatalogConfigure
from deriva.utils.catalog.manage.deriva_csv import DerivaCSV


# These need to be changed depending on the host and groups available.
host = 'demo.derivacloud.org'
catalog_name='test'
schema_name='Demo'

init_logging()
logger = logging.getLogger(__name__)


# Create a new catalog instance
def create_catalog(server):
     credentials = get_credential(server)
     catalog = DerivaServer('https', server, credentials=credentials).create_ermrest_catalog()
     catalog_id = catalog.catalog_id
     logger.info('Catalog_id is {}'.format(catalog_id))
     return catalog_id

def menu_url(schema_name, table_name):
     return {
         'name': table_name,
         'url': "/chaise/recordset/#{{{$catalog.id}}}/" + "{}:{}".format(schema_name, table_name)
     }


logger.info('Creating catalog....')
catalog_id = create_catalog(host)

logger.info('Configuring catalog....')
catalog = DerivaCatalogConfigure(host, catalog_id=catalog_id)
catalog.configure_baseline_catalog(catalog_name='test',
                                   admin='DERIVA Demo Admin',
                                   curator='DERIVA Demo Curator',
                                   writer='DERIVA Demo Writer', reader='*')

with open('about.md') as f:
    about_content = f.read()

with open('help.md') as f:
    help_content = f.read()

r = list(
    catalog['WWW']['Page'].datapath().insert(
        [
            {
                'Title': 'About the Catalog',
                'Content': about_content
            },
            {
                'Title': 'Help',
                'Content': help_content
            },
        ]
    )
)

about_rid = r[0]['RID']
help_rid = r[1]['RID']

# Set up the navigation bar.
catalog.navbar_menu = {
    'newTab': False,
    'children': [
        {'name': "Browse",
         'children': [
             menu_url(schema_name, 'Collection'),
             menu_url(schema_name, 'Study'),
             menu_url(schema_name, "Experiment"),
             menu_url(schema_name, 'Replicate'),
             menu_url(schema_name, 'Specimen'),
             menu_url(schema_name, "File"),
             menu_url(schema_name, "Imaging"),
             menu_url(schema_name, "Anatomy"),
             menu_url("WWW", "Page")
         ]
         },
        {'name': "About", 'url': '/chaise/record/#{{{$catalog.id}}}/WWW:Page/RID=' + about_rid},
        {'name': "Help", 'url': '/chaise/record/#{{{$catalog.id}}}/WWW:Page/RID=' + help_rid}
    ]
}

logger.info('Creating schema')
schema = catalog.create_schema(schema_name)

# Create Basic Tables.
with DerivaModel(catalog):
     logger.info('Creating tables....')
     study = schema.create_table('Study',
                                 [DerivaColumn.define('Title', 'text'),
                                  DerivaColumn.define('Description', 'text')])
     study.configure_table_defaults()

     experiment = schema.create_table('Experiment', [
         DerivaColumn.define('Description', 'markdown'),
         DerivaColumn.define('Experiment_Type', 'text')
     ])
     experiment.configure_table_defaults()

     replicate = schema.create_table('Replicate', [DerivaColumn.define('Replicate_Number', 'int4')])
     replicate.configure_table_defaults()

     specimen = schema.create_table('Specimen', [DerivaColumn.define('Specimen_Type', 'text')])
     specimen.configure_table_defaults()

     # Asset tables
     logger.info('Creating asset tables....')
     file = schema.create_asset('File',
                                column_defs=[
                                     DerivaColumn.define('File_Type', 'text'),
                                     DerivaColumn.define('Description', 'text')
                                ])
     file.configure_table_defaults()

     imaging = schema.create_asset('Imaging')
     imaging.configure_table_defaults()

     # Create collections.
     collection = schema.create_table('Collection',[DerivaColumn.define('Description', 'text'),
                                                    DerivaColumn.define('Name', 'text')
                                                    ])
     # Create links between tables.
     logger.info('Linking tables....')
     experiment.link_tables(study)
     replicate.link_tables(file)

     collection.associate_tables(specimen)
     collection.associate_tables(study)

     specimen.associate_tables(imaging)
     experiment.associate_tables(imaging)

     anatomy = schema.create_vocabulary('Anatomy', 'DEMO:{RID}')
     specimen.associate_vocabulary(anatomy)

# Now add some content.....
experiment_csv = DerivaCSV('Experiment.csv', schema_name)
experiment_csv.upload_to_deriva(catalog)

logger.info('Catalog %s', study.chaise_uri)

# Load files into hatrac.

