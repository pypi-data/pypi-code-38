import os
import click
import sys

from cotoba_cli.cognito import get_cognito_user
from cotoba_cli import config
from cotoba_cli import nlu


@click.group(help='nlu')
@click.option('--endpoint-url', type=str, help='Endpoint URL', default=None)
@click.pass_context
def cli_nlu(context, endpoint_url):
    if not context.obj:
        context.obj = {}
    if not endpoint_url:
        if os.environ.get('COTOBA_ENDPOINT_URL'):
            endpoint_url = os.environ.get('COTOBA_ENDPOINT_URL')
        elif config.load()['default'].get('endpoint-url'):
            endpoint_url = config.load()['default'].get('endpoint-url')
        else:
            sys.stderr.write('endpoint-url is not set.\n')
            sys.exit(1)

    context.obj['endpoint_url'] = endpoint_url


@cli_nlu.command(help='Create and upload training data.')
@click.option('--data-name', 'data_name', type=str, required=True,
              help='Name.')
@click.option('--file', 'file_path', type=str, required=True,
              help='Path to training data file.')
@click.pass_context
def create_training_data(context, data_name, file_path):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.create_training_data(cognito_user, data_name, file_path,
                                   endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Update training data description.')
@click.option('--training-data-id', 'training_data_id',
              type=str, required=True,
              help='Training data name to read.')
@click.option('--description', 'description', type=str, required=True,
              help='Description of updated content.')
@click.pass_context
def update_training_data(context, training_data_id, description):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.update_training_data(cognito_user, training_data_id, description,
                                   endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Delete training data.')
@click.option('--training-data-id', 'training_data_id',
              type=str, required=True,
              help='Training data name to read.')
@click.pass_context
def delete_training_data(context, training_data_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.delete_training_data(cognito_user, training_data_id,
                                   endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='List training data.')
@click.pass_context
def list_training_data(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.list_training_data(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read training data.')
@click.option('--training-data-id', 'training_data_id',
              type=str, required=True,
              help='Training data name to read.')
@click.pass_context
def read_training_data(context, training_data_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_training_data(cognito_user, training_data_id,
                                 endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='List algorithm.')
@click.pass_context
def list_algorithm(context):
    endpoint_url = context.obj['endpoint_url']
    res = nlu.list_algorithm(endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read algorithm hyperparameters.')
@click.option('--image-name', 'image_name', type=str, required=True,
              help='Name.')
@click.pass_context
def read_algorithm_hyper_parameter(context, image_name):
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_algorithm_hyper_parameter(image_name,
                                             endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Create and upload slot dictionary.')
@click.option('--data-name', 'data_name', type=str, required=True,
              help='Name.')
@click.option('--file', 'file_path', type=str, required=True,
              help='Path to slot dictionary file.')
@click.pass_context
def create_slot_dictionary(context, data_name, file_path):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.create_slot_dictionary(cognito_user, data_name, file_path,
                                     endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read slot dictionary.')
@click.option('--slot-dictionary-id', 'slot_dictionary_id',
              type=str, required=True,
              help='Slot dictionary name to read.')
@click.pass_context
def read_slot_dictionary(context, slot_dictionary_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_slot_dictionary(cognito_user, slot_dictionary_id,
                                   endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Delete slot dictionary.')
@click.option('--slot-dictionary-id', 'slot_dictionary_id',
              type=str, required=True,
              help='Slot dictionary name to delete.')
@click.pass_context
def delete_slot_dictionary(context, slot_dictionary_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.delete_slot_dictionary(cognito_user, slot_dictionary_id,
                                     endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Update slot dictionary description.')
@click.option('--slot-dictionary-id', 'slot_dictionary_id',
              type=str, required=True,
              help='Slot dictionary name to delete.')
@click.option('--description', 'description', type=str, required=True,
              help='Description of updated content.')
@click.pass_context
def update_slot_dictionary(context, slot_dictionary_id, description):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.update_slot_dictionary(cognito_user,
                                     slot_dictionary_id,
                                     description,
                                     endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='List slot dictionary.')
@click.pass_context
def list_slot_dictionary(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.list_slot_dictionaries(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Create model.')
@click.option('--training-data-id', 'training_data_id',
              type=str, required=True,
              help='Training data id.')
@click.option('--algorithm-name', 'algorithm_name',
              type=str, required=True,
              help='Algorithm name.')
@click.option('--job-name', 'job_name',
              type=str, required=True,
              help='Job name.')
@click.option('--slot-dictionary-id', 'slot_dictionary_id',
              type=str, required=False,
              help='Slot dictionary id.')
@click.option('--description', 'description',
              type=str, required=False,
              help='Description.')
@click.option('--instance-type', 'instance_type',
              type=str, required=False,
              help='Instance type.')
@click.option('--instance-count', 'instance_count',
              type=int, required=False,
              help='Instance count.')
@click.option('--volume-size-in-gb', 'volume_size_in_gb',
              type=int, required=False,
              help='Volume size in GB.')
@click.option('--hyper-parameters-file', 'file_path',
              type=str, required=False,
              help='Path to Hyper parameters file.')
@click.option('--hyper-parameters', 'hyper_parameters',
              type=str, required=False,
              help='Hyper parameters. Invalid when option '
                   '--hyper-parameters-file is specified.')
@click.option('--original-model-id', 'original_model_id',
              type=str, required=False,
              help='original model id for continuous learning.')
@click.pass_context
def create_model(context,
                 training_data_id,
                 algorithm_name,
                 slot_dictionary_id,
                 job_name,
                 description,
                 instance_type,
                 instance_count,
                 volume_size_in_gb,
                 file_path,
                 hyper_parameters,
                 original_model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.create_model(cognito_user,
                           training_data_id,
                           algorithm_name,
                           slot_dictionary_id,
                           job_name,
                           description,
                           instance_type,
                           instance_count,
                           volume_size_in_gb,
                           file_path,
                           hyper_parameters,
                           original_model_id,
                           endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Update model description.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.option('--description', 'description',
              type=str, required=True,
              help='Description of updated content.')
@click.pass_context
def update_model(context, model_id, description):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.update_model(cognito_user, model_id, description,
                           endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read model.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.pass_context
def read_model(context, model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_model(cognito_user, model_id, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Delete model.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.pass_context
def delete_model(context, model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.delete_model(cognito_user, model_id, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='List model.')
@click.pass_context
def list_model(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.list_models(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Create endpoint.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.option('--slot-dictionary-id', 'slot_dictionary_id',
              type=str, help='slot dictionary id.')
@click.option('--max-capacity', 'max_capacity',
              type=str, help='max capacity for auto-scaling.')
@click.pass_context
def create_endpoint(context, model_id, max_capacity, slot_dictionary_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.create_endpoint(cognito_user, model_id,
                              max_capacity,
                              slot_dictionary_id,
                              endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read possitble intents of model.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.pass_context
def read_intent(context, model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_intent(cognito_user, model_id, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read possible slots of model.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.pass_context
def read_slot(context, model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.read_slot(cognito_user, model_id, endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='delete endpoint.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.pass_context
def delete_endpoint(context, model_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = nlu.delete_endpoint(cognito_user, model_id,
                              endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Inference by using endpoint.')
@click.option('--utterance', 'utterance',
              type=str, required=True,
              help='utterance.')
@click.option('--model-id', 'model_id',
              type=str, required=True,
              help='model id.')
@click.option('--api-key', 'api_key',
              type=str, default='',
              help='api key.')
@click.option('--slot-dic', 'slot_dic',
              type=str, default='',
              help='slot dic json.')
@click.pass_context
def inference(context, utterance, model_id, api_key, slot_dic):
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    res = nlu.inference(cognito_user,
                        utterance,
                        model_id,
                        api_key=api_key,
                        slot_dic=slot_dic,
                        endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Get endpoint url.')
@click.option('--endpoint-id', 'endpoint_id',
              type=str, required=True,
              help='endpoint_id.')
@click.option('--api-key', 'api_key',
              type=str, default='',
              help='api_key.')
@click.pass_context
def get_endpoint_url(context, endpoint_id, api_key):
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    res = nlu.get_endpoint_url(cognito_user,
                               endpoint_id,
                               api_key=api_key,
                               endpoint_url=endpoint_url)
    res.print()


@cli_nlu.command(help='Read remaining resources.')
@click.pass_context
def read_remaining_resources(context):
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    res = nlu.read_remaining_resources(cognito_user,
                                       endpoint_url=endpoint_url)
    res.print()
