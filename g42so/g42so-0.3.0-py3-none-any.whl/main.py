#!/usr/bin/env python
# coding: utf-8

import argparse
import sys
import logging

from . import generate_library, find_classes, __version__

def main():
    parser = argparse.ArgumentParser(
        description='Convert source code for a Geant4 detector construction '
                    'into a geometry that can be read by TRIPOLI-4®.',
        epilog='Any options after `--\' will be passed to the compiler.'
        )

    # general arguments
    g_general = parser.add_argument_group('general arguments')
    g_general.add_argument('-v', '--verbose', help='increase verbosity',
                        action='count', default=0)
    g_general.add_argument('-V', '--version',
                        action='version', version=__version__)
    g_general.add_argument('-o', '--output', metavar='OUTPUT_FILE',
                        help='name of the file to generate')
    g_general.add_argument('-I', '--include', metavar='INCLUDE_DIR',
                        help='directories to search for header files (may be '
                                'specified multiple times)',
                        action='append', default=[])
    g_general.add_argument('-c', '--compiler', metavar='COMPILER_PATH',
                        help='path to the compiler that should be used')
    g_general.add_argument('-e', '--encoding', metavar='ENCODING',
                        help='character encoding for geant4-config output',
                        default='utf-8')
    g_general.add_argument('--geant4-config',
                        help='path to the geant4-config executable')
    g_general.add_argument('sources', metavar='source_file', nargs='*',
                        help='source files')


    # detector args
    g_detector = parser.add_argument_group('detector arguments')
    g_detector.add_argument('-d', '--detector', metavar='DETECTOR_CLASS',
                            help='name of the detector-construction class')
    g_detector.add_argument('--dump-detector-wrapper',
                            help='dump (to stdout) a template for custom wrapper '
                                'functions for the detector class',
                            action='store_true')
    g_detector.add_argument('--custom-detector-wrapper',
                            help='use this if you are providing your custom '
                                'wrapper for detector construction as a source '
                                'file. If this option is not specified, %(prog)s '
                                'will automatically generate a wrapper.',
                            action='store_true')

    # pga args
    g_pga = parser.add_argument_group('primary-generator-action arguments')
    g_pga.add_argument('--without-pga', action='store_true',
                    help='do not compile the primary generator action',
                    default=False)
    g_pga.add_argument('-p', '--primary-generator-action', metavar='PGA_CLASS',
                    help='name of the primary-generator-action class')
    g_pga.add_argument('--dump-pga-wrapper',
                    help='dump (to stdout) a template for custom wrapper '
                            'functions for the primary generator action class',
                    action='store_true')
    g_pga.add_argument('--custom-pga-wrapper',
                    help='use this if you are providing your custom wrapper '
                            'for the primary generator action as a source file. '
                            'If this option is not specified, %(prog)s will '
                            'automatically generate a wrapper.',
                            action='store_true')

    # parse the arguments
    # limit argument parsing to args before --
    last_arg_to_parse = next((i for i, v in enumerate(sys.argv) if v == '--'),
                            len(sys.argv))
    args = parser.parse_args(sys.argv[1:last_arg_to_parse])
    remaining_args = sys.argv[last_arg_to_parse+1:]

    # dump the detector wrapper template
    if args.dump_detector_wrapper:
        print(generate_library.get_dummy_g42so_detector_wrapper_functions())
        sys.exit(0)

    # dump the wrapper template
    if args.dump_pga_wrapper:
        print(generate_library.get_dummy_g42so_pga_wrapper_functions())
        sys.exit(0)

    # check for the presence of source files
    if not args.sources:
        parser.error('too few arguments')

    # define the logger
    logging.basicConfig(level=logging.INFO - 10*args.verbose)

    # process the options
    header_suffixes = ['.hh', '.hpp', '.h', '.hxx']

    # process the -d option -- either take the supplied class name or detect it
    if args.detector:
        detector = args.detector
        detector_wheader = (
            detector,
            find_classes.find_header_for_class(
                detector,
                dirs=args.include,
                suffixes=header_suffixes
                )
            )
    else:
        detector_wheader = find_classes.find_in_dirs(
            base='G4VUserDetectorConstruction',
            dirs=args.include,
            suffixes=header_suffixes,
            many=False,
            required=True
            )

    # process the -p option, if supplied
    if not args.without_pga:
        if args.primary_generator_action:
            pga = args.primary_generator_action
            pga_wheader = (
                pga,
                find_classes.find_header_for_class(
                    pga,
                    dirs=args.include,
                    suffixes=header_suffixes
                    )
                )
        else:
            pga_wheader = find_classes.find_in_dirs(
                base='G4VUserPrimaryGeneratorAction',
                dirs=args.include,
                suffixes=header_suffixes,
                many=False,
                required=False)
    else:
        pga_wheader = ()

    generate_library.compile(
        args.sources,
        args.include,
        detector_wheader,
        pga_wheader,
        output=args.output,
        other_flags=remaining_args,
        g4config_path=args.geant4_config,
        custom_detector_wrapper=args.custom_detector_wrapper,
        custom_pga_wrapper=args.custom_pga_wrapper,
        compiler=args.compiler,
        encoding=args.encoding
        )

if __name__ == '__main__':
    main()
