from ..sdk_impl import create_flywheel_client

"""


Usage:
  fw export bids [dest folder] [flags]

Flags:
      --data-type stringArray   Limit export to the given data-types (e.g. func)
      --source-data             Include sourcedata in BIDS export
"""
def add_command(subparsers, parents):
    parser = subparsers.add_parser('bids', parents=parents, help='Export a BIDS project to the destination folder')
    parser.add_argument('folder', metavar='[dest folder]', help='The path to the destination folder')
    parser.add_argument('--project', '-p', required=True, help='Label of project to import into')
    parser.add_argument('--subject', dest='subjects', action='append', help='Limit export to the given subject')
    parser.add_argument('--session', dest='sessions', action='append', help='Limit export to the given session')
    parser.add_argument('--data-type', dest='data_types', action='append', help='Limit export to the given data-types. (e.g. func)')
    parser.add_argument('--source-data', action='store_true', help='Include sourcedata in BIDS export')

    parser.set_defaults(func=export_bids)
    parser.set_defaults(parser=parser)

    return parser

def export_bids(args):
    import flywheel_bids.export_bids

    fw = create_flywheel_client()
    flywheel_bids.export_bids.export_bids(fw, args.folder, args.project, subjects=args.subjects, sessions=args.sessions, 
        folders=args.data_types, source_data=args.source_data, validate=False)


