#pylint: disable=missing-docstring,redefined-outer-name,invalid-name,broad-except
"""
*hynet* command line tool.
"""

import argparse

import hynet as ht


def command_test(args):  # pylint: disable=unused-argument
    if ht.test_installation():
        print("\nAll installed solvers work properly.")
    else:
        print("\nTest failed. Please check the installation.")
        raise SystemExit(1)


def command_import(args):
    try:
        output_file = \
            ht.import_matpower_test_case(input_file=args.file_name,
                                         output_file=args.output,
                                         grid_name=args.grid_name,
                                         description=args.description,
                                         num_sample_points=args.num_sample_points,
                                         res_detection=args.res_detection)
    except Exception as exception:
        print("ERROR: " + str(exception))
        print("Failed to import '{:s}'.".format(args.file_name))
        raise SystemExit(1)
    else:
        print("Successfully imported to '{:s}'.".format(output_file))


def command_client(args):
    if args.num_workers is None:
        if ht.config.DISTRIBUTED['default_num_workers'] > 1:
            ht.config.GENERAL['parallelize'] = False
    elif args.num_workers > 1:
        ht.config.GENERAL['parallelize'] = False
    try:
        ht.start_optimization_client(server_ip=args.server_ip,
                                     port=args.port,
                                     authkey=args.authkey,
                                     num_workers=args.num_workers)
    except KeyboardInterrupt:
        pass  # Terminated by the user
    except Exception as exception:
        print("ERROR: " + str(exception))
        raise SystemExit(1)


def command_opf(args):
    if args.type:
        args.type = ht.SolverType(args.type)
    try:
        print(ht.calc_opf(ht.connect(args.database),
                          scenario_id=args.scenario,
                          solver_type=args.type))
    except Exception as exception:
        print("ERROR: " + str(exception))
        raise SystemExit(1)


parser = argparse.ArgumentParser(
    description="An optimal power flow framework for hybrid AC/DC power systems.",
    prog='python -m hynet')
parser.add_argument(
    '-v', '--version',
    action='store_true',
    help="show the program version and exit")
subparsers = parser.add_subparsers()

parser_test = subparsers.add_parser(
    'test',
    help='test the installation')
parser_test.set_defaults(execute_command=command_test)

parser_imp = subparsers.add_parser(
    'import',
    help="import data into the hynet grid database format",
    formatter_class=argparse.RawTextHelpFormatter)
parser_imp.add_argument(
    'file_name',
    type=str,
    help="MATPOWER test case as MATLAB MAT-file with 'mpc'")
parser_imp.add_argument(
    '-o', '--output',
    type=str,
    help="output file name\n(default: input file name with a '.db' extension)")
parser_imp.add_argument(
    '-g', '--grid_name',
    type=str,
    default=None,
    help="name of the grid\n(default: input file name without the extension)")
parser_imp.add_argument(
    '-d', '--description',
    type=str,
    default='',
    help="description and copyright/licensing information")
parser_imp.add_argument(
    '-n', '--num_sample_points',
    type=int,
    default=10,
    help="sample points for polynomial to PWL conversion\n(default: 10)")
parser_imp.add_argument(
    '-r', '--res_detection',
    action='store_true',
    help="enable RES injector type detection")
parser_imp.set_defaults(execute_command=command_import)

parser_client = subparsers.add_parser(
    'client',
    help="start a hynet optimization client on this machine")
parser_client.add_argument(
    'server_ip',
    type=str,
    help="IP address of the hynet optimization server")
parser_client.add_argument(
    '-p', '--port',
    type=int,
    default=None,
    help="TCP port number of the hynet optimization server")
parser_client.add_argument(
    '-a', '--authkey',
    type=str,
    default=None,
    help="authentication key for the hynet optimization server")
parser_client.add_argument(
    '-n', '--num_workers',
    type=int,
    default=None,
    help="number of worker processes that should run in parallel")
parser_client.set_defaults(execute_command=command_client)

parser_opf = subparsers.add_parser(
    'opf',
    help="calculate an optimal power flow")
parser_opf.add_argument(
    'database',
    type=str,
    help="file name of the grid database")
parser_opf.add_argument(
    '-s', '--scenario',
    metavar='ID',
    type=int,
    default=0,
    help="specify the scenario ID")
parser_opf.add_argument(
    '-t', '--type',
    type=str.upper,
    choices=['QCQP', 'SDR', 'SOCR'],
    help="specify the solver type")
parser_opf.set_defaults(execute_command=command_opf)

args = parser.parse_args()

if args.version:
    print("hynet v" + ht.__version__)
elif hasattr(args, 'execute_command'):
    try:
        args.execute_command(args)
    except Exception as exception:
        print(exception)
else:
    parser.print_usage()
