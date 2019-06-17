
from ..importers.bruker_scan import create_bruker_scanner

def add_command(subparsers, parents):
    parser = subparsers.add_parser('bruker', parents=parents, help='Import structured bruker data')
    parser.add_argument('folder', help='The path to the folder to import')
    parser.add_argument('group', metavar='group_id', help='The id of the group')
    parser.add_argument('project', metavar='project_label', help='The label of the project')

    parser.add_argument('--folder-template', help='The optional folder template')

    parser.set_defaults(func=import_bruker_folder)
    parser.set_defaults(parser=parser)

    return parser

def import_bruker_folder(args):
    # Build the importer instance
    importer = create_bruker_scanner(args.group, args.project, args.symlinks, args.config, 
            folder_template=args.folder_template)

    # Perform the import
    importer.interactive_import(args.folder)

