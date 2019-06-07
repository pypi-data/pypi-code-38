# coding=utf-8
from __future__ import print_function
import argparse
import urllib3
import logging
from ibm_ai_openscale_cli.enums import ResetType, MLEngineType
from ibm_ai_openscale_cli import logging_temp_file, name
from ibm_ai_openscale_cli.environments import Environments
from ibm_ai_openscale_cli.openscale_ops import OpenScaleOps
from ibm_ai_openscale_cli.reset_ops import ResetOps
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.version import __version__
from outdated import warn_if_outdated

logger = FastpathLogger(__name__)

SERVICE_NAME = 'Watson OpenScale'

def get_argument_parser():
    """
    generate a CLI arguments parser
    Returns:
       argument parser
    """
    description ='IBM Watson Openscale "express path" configuration tool. This tool allows the user to get started quickly with Watson OpenScale: 1) If needed, provision a Lite plan instance for IBM Watson OpenScale\n2) If needed, provision a Lite plan instance for IBM Watson Machine Learning\n3) Drop and re-create the IBM Watson OpenScale datamart instance and datamart database schema\n4) Optionally, deploy a sample machine learning model to the WML instance\n5) Configure the sample model instance to OpenScale, including payload logging, fairness checking, feedback, quality checking, and explainability\n6) Optionally, store up to 7 days of historical payload, fairness, and quality data for the sample model'
    parser = argparse.ArgumentParser(description=description)
    # required parameters
    required_args_group = parser.add_argument_group('required arguments (only one needed)')
    required_args = required_args_group.add_mutually_exclusive_group(required=True)
    required_args.add_argument('-a', '--apikey', help='IBM Cloud platform user APIKey. If "--env icp" is also specified, APIKey value is not used.')
    required_args.add_argument('-i', '--iam-token', help='IBM Cloud authentication IAM token, or IBM Cloud private authentication IAM token. Format can be (--iam-token "Bearer <token>") or (--iam-token <token>)')
    # Optional parameters
    optional_args = parser._action_groups.pop()
    parser.add_argument('--env', default='ypprod', help='Environment. Default "ypprod"', choices=['ypprod', 'ypqa', 'ys1dev', 'icp'])
    parser.add_argument('--resource-group', default='default', help='Resource Group to use. If not specified, then "default" group is used')
    parser.add_argument('--postgres', help='Path to postgres credentials file for the datamart database. If --postgres, --icd, and --db2 all are not specified, then the internal {} database is used'.format(SERVICE_NAME))
    parser.add_argument('--postgres-json', help='Postgres credentials in JSON format')
    parser.add_argument('--icd', help='Path to IBM Cloud Database credentials file for the datamart database')
    parser.add_argument('--icd-json', help='IBM Cloud Database credentials for the datamart database in JSON format')
    parser.add_argument('--db2', help='Path to IBM DB2 credentials file for the datamart database')
    parser.add_argument('--db2-json', help='IBM DB2 credentials for the datamart database in JSON format:  \'{"username":"<USERNAME>","password":"<PASSWORD>","hostname":"<hostname>","port":"<port>","db":"<db>","ssl":"Optional - set to true if db2 connection should use ssl. Default is false","certificate_base64":"Optional - Base64 encoded SSL certificate, required when using self signed certificates"}\'')
    parser.add_argument('--wml', help='Path to IBM WML credentials file')
    parser.add_argument('--wml-json', help='IBM WML credentials in JSON format')
    parser.add_argument('--azure', help='Path to Microsoft Azure credentials file')
    parser.add_argument('--azure-json', help='Microsoft Azure credentials in JSON format: \'{ "client_id": "<CLIENT_ID", "client_secret": "<CLIENT_SECRET", "tenant": "<TENANT>", "subscription_id": "<SUBSCRIPTION_ID" }\'')
    parser.add_argument('--spss', help='Path to SPSS credentials file')
    parser.add_argument('--spss-json', help='SPSS credentials in JSON format: \'{ "username": "<USERNAME>", "password": "<PASSWORD", "url": "<URL>" }\'')
    parser.add_argument('--custom', help='Path to Custom Engine credentials file')
    parser.add_argument('--custom-json', help='Custom Engine credentials in JSON format: \'{ "url": "<URL>" }\'')
    parser.add_argument('--aws', help='Path to Amazon Web Services credentials file')
    parser.add_argument('--aws-json', help='Amazon Web Services credentials in JSON format: \'{ "access_key_id": "<ACCESS_KEY_ID", "secret_access_key": "<SECRET_ACCESS_KEY", "region": "<REGION>" }\'')
    parser.add_argument('--deployment-name', help='Name of the existing deployment to use. Required for Azure ML Studio, SPSS Engine and Custom ML Engine, but optional for Watson Machine Learning. Required for custom models')
    parser.add_argument('--keep-schema', action='store_true', help='Use pre-existing datamart schema, only dropping all tables. If not specified, datamart schema is dropped and re-created')
    parser.add_argument('--username', help='ICP username. Required if "icp" environment is chosen, not required if --iam-token is specified')
    parser.add_argument('--password', help='ICP password. Required if "icp" environment is chosen, not required if --iam-token is specified')
    parser.add_argument('--url', help='ICP url. Required if "icp" environment is chosen')
    parser.add_argument('--datamart-name', help='Specify data mart name and database schema, default is the datamart database connection username. For internal database, the default is "wosfastpath"')
    parser.add_argument('--history', default=7, help='Days of history to preload. Default is 7', type=int)
    parser.add_argument('--history-only', action='store_true', help='Store history only for existing deployment and datamart. Requires --extend and --deployment-name also be specified')
    parser.add_argument('--history-first-day', default=0, help='Starting day for history. Default is 0', type=int)
    parser.add_argument('--model', default='GermanCreditRiskModel', help='Sample model to set up with Watson OpenScale (default "GermanCreditRiskModel")', choices=['all', 'GermanCreditRiskModel', 'DrugSelectionModel', 'GolfModel'])
    parser.add_argument('--custom-model', help='Name of custom model to set up with Watson OpenScale. If specified, overrides the value set by --model. Also requires that --custom-model-directory')
    parser.add_argument('--custom-model-directory', help='Directory with model configuration and metadata files. Also requires that --custom-model be specified')
    parser.add_argument('--extend', action='store_true', help='Extend existing datamart, instead of deleting and recreating it')
    parser.add_argument('--protect-datamart', action='store_true', help='If specified, the setup will exit if an existing datamart setup is found')
    parser.add_argument('--reset', choices=['metrics', 'monitors', 'datamart', 'model', 'all'], help='Reset existing datamart and/or sample models then exit')
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))

    # undocumented optional arguments
    parser.add_argument('--training-data-json', help=argparse.SUPPRESS)
    parser.add_argument('--bx', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--model-first-instance', default=1, help=argparse.SUPPRESS, type=int) # First "instance" (copy) of each model. Default 1 means to start with the base model instance
    parser.add_argument('--model-instances', default=1, help=argparse.SUPPRESS, type=int) # Number of additional instances beyond the first.
    parser.add_argument('--pause-between-models', default=0.0, help=argparse.SUPPRESS, type=float) # Pause in seconds between main loops. Intended to help stagger fairness checks more evenly.
    parser.add_argument('--score-columns', action='store_true', help=argparse.SUPPRESS) # If true, generate score requests with random values from the training data columns. The default is to score with values from random rows from the training data
    parser.add_argument('--num-scores', default=100, help=argparse.SUPPRESS, type=int) # Number of live scoring requests to generate. Default is 100
    parser.add_argument('--values-per-score', default=1, help=argparse.SUPPRESS, type=int) # Number of scores per score request. Default is 1, and value cannot be 0. Values greater than 1 only supported for WML deployments
    parser.add_argument('--pause-between-scores', default=0.0, help=argparse.SUPPRESS, type=float) # Pause in seconds between score requests. Only applicable to WML deployments
    parser.add_argument('--sync-checks', action='store_true', help=argparse.SUPPRESS) # If true, make fairness and quality checks synchronous (default is asynchronous)
    parser.add_argument('--no-checks', action='store_true', help=argparse.SUPPRESS) # If true, skip the fairness and quality checks
    parser.add_argument('--num-explains', default=0, help=argparse.SUPPRESS, type=int) # Number of explain requests. Default is 0
    parser.add_argument('--max-explain-candidates', default=0, help=argparse.SUPPRESS, type=int) # Maximum number of candidate scores for explain. Default is 0
    parser.add_argument('--explain-start-sync', action='store_true', help=argparse.SUPPRESS) # After getting explain candidates, user input requred before sending explain requests
    parser.add_argument('--pause-between-explains', default=0.0, help=argparse.SUPPRESS, type=float) # Pause in seconds between explain requests.
    parser.add_argument('--sync-explains', action='store_true', help=argparse.SUPPRESS) # If true, make explain requests synchronous (default is asynchronous)
    parser.add_argument('--explain-no-cem', action='store_true', help=argparse.SUPPRESS) # If true, don't include cem "contrastive" explains, but lime only (default is both lime and cem)
    parser.add_argument('--organization', help=argparse.SUPPRESS, required=False)
    parser.add_argument('--space', help=argparse.SUPPRESS, required=False)
    parser._action_groups.append(optional_args)
    return parser

def log_error_raise_exception(error_msg):
    logger.log_error(error_msg)
    raise Exception(error_msg)

def initialize(args):
    """
    Initialize and validate necessary entities
    """
    def _validate_deployment_name_specified(deployment_name, model_name=None, env_name='ypprod'):
        if args.ml_engine_type is MLEngineType.WML:
            if deployment_name and model_name == 'all':
                log_error_raise_exception('ERROR: A model name is required when a deployment is specified for {}'.format(args.ml_engine_type.value))
        else:
            if not deployment_name:
                log_error_raise_exception('ERROR: A deployment name is required when {} is used with {}'.format(SERVICE_NAME, args.ml_engine_type.value))

    def _validate_is_icp(env_name):
        if not env_name == 'icp':
            log_error_raise_exception('ERROR: {} is only supported on {} on IBM Cloud Private (ICP)'.format(args.ml_engine_type.value, SERVICE_NAME))

    def _validate_db_provided(postgres, icd, db2):
        if not (postgres or icd or db2):
            log_error_raise_exception('ERROR: Database must be provided to setup {} on IBM Cloud Private (ICP)'.format(SERVICE_NAME))

    # token
    if args.iam_token:
        array = args.iam_token.split(' ')
        if array:
            if len(array) == 2 and array[0].lower().startswith('bearer'):
                args.iam_token = array[1]

    # validate environment
    if 'throw' in args:
        log_error_raise_exception(args.throw)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('handle_response').setLevel(logging.DEBUG)
        logging.getLogger('ibm_ai_openscale.utils.client_errors').setLevel(logging.DEBUG)

    # setup the loger
    logger.log_info('ibm-ai-openscale-cli-{}'.format(__version__))
    logger.log_info('Log file: {0}'.format(logging_temp_file.name))

    # outdated packages
    warn_if_outdated(name, __version__)

    # initialize args
    args.is_icp = False
    args.service_name = SERVICE_NAME
    if args.azure or args.azure_json:
        args.ml_engine_type = MLEngineType.AZUREML
        _validate_deployment_name_specified(args.deployment_name)
    elif args.spss or args.spss_json:
        args.ml_engine_type = MLEngineType.SPSS
        _validate_is_icp(args.env)
        _validate_deployment_name_specified(args.deployment_name)
    elif args.custom or args.custom_json:
        args.ml_engine_type = MLEngineType.CUSTOM
        _validate_deployment_name_specified(args.deployment_name)
    elif args.aws or args.aws_json:
        args.ml_engine_type = MLEngineType.SAGEMAKER
        _validate_deployment_name_specified(args.deployment_name)
    else:
        args.ml_engine_type = MLEngineType.WML
        _validate_deployment_name_specified(args.deployment_name, args.model, args.env)
    env_dict = Environments(args).get_attributes()
    args.env_dict = env_dict
    if args.reset:
        args.reset_type = ResetType(args.reset)
    if args.env == 'icp':
        _validate_db_provided(args.postgres, args.icd, args.db2)
        args.is_icp = True
        logger.log_info('SSL verification is not used for requests against ICP Environment, disabling "InsecureRequestWarning"')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if args.history_only and (not args.deployment_name or not args.extend):
        log_error_raise_exception('ERROR: --history-only requires that both --extend and --deployment-name also be specified')
    if args.values_per_score > 1 and not args.ml_engine_type == MLEngineType.WML:
        log_error_raise_exception('ERROR: Only WML supports more than 1 value per score request')
    if args.values_per_score < 1:
        log_error_raise_exception('ERROR: Values per score request must be at least 1')

def show_finish_prompt(dashboard_url):
    logger.log_info('Process complete')
    if dashboard_url.startswith('https://api.'):
        dashboard_url = dashboard_url.replace('https://api.', 'https://')
    logger.log_info('The {} dashboard can be accessed at: {}/aiopenscale'.format(SERVICE_NAME, dashboard_url))

def main(arguments=None):

    args = arguments if arguments else get_argument_parser().parse_args()
    initialize(args)

    # operations
    if args.reset:
        ResetOps(args).execute()
    else:
        OpenScaleOps(args).execute()

    # finish
    show_finish_prompt(args.env_dict['aios_url'])
