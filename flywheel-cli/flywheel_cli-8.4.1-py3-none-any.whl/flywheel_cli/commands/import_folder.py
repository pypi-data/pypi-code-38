import argparse
import re
import textwrap

from ..importers import FolderImporter, StringMatchNode

def add_command(subparsers, parents):
    parser = subparsers.add_parser('folder', parents=parents, help='Import a structured folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Import a folder with the following structure:

            root-folder
            └── group-id
                └── project-label
                    └── subject-label
                        └── session-label
                            └── acquisition-label
                                ├── dicom
                                │   ├── 1.dcm
                                │   └── 2.dcm
                                ├── data.foo
                                └── scan.nii.gz

            Files can be placed at the project level and below.

            By default, folders under the acquisition label will be zipped with
                foldername as the default.
            """))
    parser.add_argument('folder', help='The path to the folder to import')
    parser.add_argument('--group', '-g', metavar='<id>', help='The id of the group, if not in folder structure')
    parser.add_argument('--project', '-p', metavar='<label>', help='The label of the project, if not in folder structure')

    # Cannot specify dicom folder name with dicom-acquistions, or bruker-acquisitions with either
    acq_group = parser.add_mutually_exclusive_group()
    acq_group.add_argument('--dicom', default='dicom', metavar='name', help='The name of dicom subfolders to be zipped prior to upload')
    acq_group.add_argument('--pack-acquisitions', metavar='type', help='Acquisition folders only contain acquisitions of <type> and are zipped prior to upload')

    parser.add_argument('--repack', action='store_true', help='Whether or not to validate, de-identify and repackage zipped packfiles')

    no_level_group = parser.add_mutually_exclusive_group()
    no_level_group.add_argument('--no-subjects', action='store_true', help='no subject level (create a subject for every session)')
    no_level_group.add_argument('--no-sessions', action='store_true', help='no session level (create a session for every subject)')

    parser.add_argument('--root-dirs', type=int, default=0, help='The number of directories to discard before matching')

    parser.set_defaults(func=import_folder)
    parser.set_defaults(parser=parser)

    return parser

def import_folder(args):
    # Validate that if project is set, then group is set
    if args.project and not args.group:
        args.parser.error('Specifying project requires also specifying group')

    # Build the importer instance
    importer = FolderImporter(group=args.group, project=args.project, repackage_archives=args.repack, 
        merge_subject_and_session=(args.no_subjects or args.no_sessions), config=args.config)

    for i in range(args.root_dirs):
        importer.add_template_node(StringMatchNode(re.compile('.*'))) 

    if not args.group:
        importer.add_template_node(StringMatchNode('group'))

    if not args.project:
        importer.add_template_node(StringMatchNode('project'))

    if not args.no_subjects:
        importer.add_template_node(StringMatchNode('subject'))

    if not args.no_sessions:
        importer.add_template_node(StringMatchNode('session'))

    if args.pack_acquisitions:
        importer.add_template_node(StringMatchNode('acquisition', packfile_type=args.pack_acquisitions))
    else:
        importer.add_template_node(StringMatchNode('acquisition'))
        importer.add_template_node(StringMatchNode(re.compile(args.dicom), packfile_type='dicom'))

    # Perform the import
    importer.interactive_import(args.folder)

