import jsonschema
from time import time

from flask import jsonify, request
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound, InternalServerError
from bson.objectid import ObjectId

from cc_core.commons.schemas.red import red_schema
from cc_core.commons.engines import engine_validation
from cc_core.commons.templates import get_template_keys, get_secret_values, normalize_keys
from cc_core.commons.exceptions import exception_format
from cc_core.commons.red_to_blue import convert_red_to_blue

from cc_agency.commons.helper import str_to_bool
from cc_agency.commons.secrets import separate_secrets_batch, separate_secrets_experiment


def _prepare_red_data(data, user):
    timestamp = time()

    experiment = {
        'username': user['username'],
        'registrationTime': timestamp,
        'redVersion': data['redVersion'],
        'cli': data['cli'],
        'container': data['container'],
        'protectedKeysVoided': False
    }

    if 'execution' in data:
        stripped_settings = {}

        for key, val in data['execution']['settings'].items():
            if key == 'access':
                continue

            stripped_settings[key] = val

        experiment['execution'] = {
            'engine': data['execution']['engine'],
            'settings': stripped_settings
        }

    experiment, secrets = separate_secrets_experiment(experiment)

    if 'batches' in data:
        raw_batches = data['batches']
    else:
        raw_batches = [{
            'inputs': data['inputs'],
            'outputs': data['outputs']
        }]

    batches = []

    for i, rb in enumerate(raw_batches):
        batch = {
            'username': user['username'],
            'registrationTime': timestamp,
            'state': 'registered',
            'batchesListIndex': i,
            'protectedKeysVoided': False,
            'notificationsSent': False,
            'node': None,
            'history': [{
                'state': 'registered',
                'time': timestamp,
                'debugInfo': None,
                'node': None,
                'ccagent': None
            }],
            'attempts': 0,
            'inputs': rb['inputs'],
            'outputs': rb['outputs']
        }
        batch, additional_secrets = separate_secrets_batch(batch)
        secrets.update(additional_secrets)
        batches.append(batch)

    return experiment, batches, secrets


def red_routes(app, mongo, auth, controller, trustee_client):
    @app.route('/red', methods=['POST'])
    def post_red():
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        if not request.json:
            raise BadRequest('Did not send RED data as JSON.')

        data = request.json

        try:
            jsonschema.validate(data, red_schema)
        except Exception:
            raise BadRequest('Given RED data does not comply with jsonschema. '
                             'Consider using the FAICE commandline tools for local validation.')

        template_keys = set()
        get_template_keys(data, template_keys)
        if template_keys:
            raise BadRequest(
                'The given red data contains the following variables: "{}". Please resolve them before submitting'
                ' to agency. Consider using CC-FAICE (faice exec).'.format(', '.join(template_keys)))

        secret_values = get_secret_values(data)

        if 'batches' in data:
            for batch in data['batches']:
                if 'outputs' not in batch:
                    raise BadRequest(
                        'CC-Agency requires all batches to have outputs defined. At least one batch does not comply.'
                    )

        elif 'outputs' not in data:
            raise BadRequest('CC-Agency requires outputs to be defined in RED data.')

        try:
            engine_validation(data, 'container', ['docker', 'nvidia-docker'])
        except Exception:
            raise BadRequest('\n'.join(exception_format(secret_values=secret_values)))

        if 'ram' not in data['container']['settings']:
            raise BadRequest('CC-Agency requires \'ram\' to be defined in the container settings.')

        if (data['container']['engine'] == 'nvidia-docker') and ('gpus' not in data['container']['settings']):
            raise BadRequest(
                'CC-Agency with \'nvidia-docker\' engine requires \'gpus\' to be defined in the container settings.'
            )

        try:
            engine_validation(data, 'execution', ['ccagency'], optional=True)
            normalize_keys(data)
            _ = convert_red_to_blue(data)
        except Exception:
            raise BadRequest('\n'.join(exception_format(secret_values=secret_values)))

        experiment, batches, secrets = _prepare_red_data(data, user)

        response = trustee_client.store(secrets)
        if response['state'] == 'failed':
            raise InternalServerError('Trustee service failed:\n{}'.format(response['debug_info']))

        bson_experiment_id = mongo.db['experiments'].insert_one(experiment).inserted_id
        experiment_id = str(bson_experiment_id)

        for batch in batches:
            batch['experimentId'] = experiment_id

        mongo.db['batches'].insert_many(batches)

        controller.send_json({'destination': 'scheduler'})

        return jsonify({'experimentId': experiment_id})

    @app.route('/batches/<object_id>', methods=['DELETE'])
    def delete_batches(object_id):
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        try:
            bson_id = ObjectId(object_id)
        except Exception:
            raise BadRequest('Not a valid BSON ObjectId.')

        match = {'_id': bson_id}
        match_with_state = {'_id': bson_id, 'state': {'$nin': ['succeeded', 'failed', 'cancelled']}}

        if not user['is_admin']:
            match['username'] = user['username']
            match_with_state['username'] = user['username']

        o = mongo.db['batches'].find_one(match, {'state': 1})
        if not o:
            raise NotFound('Could not find Object.')

        mongo.db['batches'].update_one(
            match_with_state,
            {
                '$set': {
                    'state': 'cancelled'
                },
                '$push': {
                    'history': {
                        'state': 'cancelled',
                        'time': time(),
                        'debugInfo': None,
                        'node': None,
                        'ccagent': None
                    }
                }
            })

        o = mongo.db['batches'].find_one(match)
        o['_id'] = str(o['_id'])

        controller.send_json({'destination': 'scheduler'})

        return jsonify(o)

    @app.route('/experiments/count', methods=['GET'])
    def get_experiments_count():
        return get_collection_count('experiments')

    @app.route('/experiments', methods=['GET'])
    def get_experiments():
        return get_collection('experiments')

    @app.route('/experiments/<object_id>', methods=['GET'])
    def get_experiments_id(object_id):
        return get_collection_id('experiments', object_id)

    @app.route('/batches/count', methods=['GET'])
    def get_batches_count():
        return get_collection_count('batches')

    @app.route('/batches', methods=['GET'])
    def get_batches():
        return get_collection('batches')

    @app.route('/batches/<object_id>', methods=['GET'])
    def get_batches_id(object_id):
        return get_collection_id('batches', object_id)

    def get_collection_id(collection, object_id):
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        try:
            bson_id = ObjectId(object_id)
        except Exception:
            raise BadRequest('Not a valid BSON ObjectId.')

        match = {'_id': bson_id}

        if not user['is_admin']:
            match['username'] = user['username']

        o = mongo.db[collection].find_one(match)
        if not o:
            raise NotFound('Could not find Object.')

        o['_id'] = str(o['_id'])
        return jsonify(o)

    def get_collection_count(collection):
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        username = request.args.get('username', default=None, type=str)
        node = None
        experiment_id = None
        state = None

        if collection == 'batches':
            node = request.args.get('node', default=None, type=str)
            state = request.args.get('state', default=None, type=str)
            experiment_id = request.args.get('experimentId', default=None, type=str)

            if experiment_id:
                try:
                    _ = ObjectId(experiment_id)
                except Exception:
                    raise BadRequest('Experiment is not a valid BSON ObjectId.')

        aggregate = []

        if not user['is_admin']:
            aggregate.append({'$match': {'username': user['username']}})

        match = {}

        if username:
            match['username'] = username

        if node:
            match['node'] = node

        if experiment_id:
            match['experimentId'] = experiment_id

        if state:
            match['state'] = state

        aggregate.append({'$match': match})
        aggregate.append({'$count': 'count'})

        cursor = mongo.db[collection].aggregate(aggregate)
        cursor = list(cursor)
        
        if not cursor:
            return jsonify({'count': 0})

        return jsonify(cursor[0])

    def get_collection(collection):
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        skip = request.args.get('skip', default=None, type=int)
        limit = request.args.get('limit', default=None, type=int)
        username = request.args.get('username', default=None, type=str)
        ascending = str_to_bool(request.args.get('ascending', default=None, type=str))

        node = None
        experiment_id = None
        state = None

        if collection == 'batches':
            node = request.args.get('node', default=None, type=str)
            state = request.args.get('state', default=None, type=str)

            states = ['registered', 'scheduled', 'processing', 'succeeded', 'failed', 'cancelled']
            if state and state not in states:
                raise BadRequest('Given state is not valid. Must be one of {}.'.format(states))

            experiment_id = request.args.get('experimentId', default=None, type=str)

            if experiment_id:
                try:
                    _ = ObjectId(experiment_id)
                except Exception:
                    raise BadRequest('Experiment is not a valid BSON ObjectId.')

        aggregate = []

        if not user['is_admin']:
            aggregate.append({'$match': {'username': user['username']}})

        match = {}

        if username:
            match['username'] = username

        if node:
            match['node'] = node

        if experiment_id:
            match['experimentId'] = experiment_id

        if state:
            match['state'] = state

        aggregate.append({'$match': match})

        aggregate.append({'$project': {
            'username': 1,
            'registrationTime': 1,
            'state': 1,
            'experimentId': 1,
            'node': 1,
            'batchesListIndex': 1
        }})

        aggregate.append({'$sort': {'registrationTime': 1 if ascending else -1}})

        if skip is not None:
            if skip < 0:
                raise BadRequest('skip cannot be lower than 0.')
            aggregate.append({'$skip': skip})

        if limit is not None:
            if limit < 1:
                raise BadRequest('limit cannot be lower than 1.')
            aggregate.append({'$limit': limit})

        cursor = mongo.db[collection].aggregate(aggregate)

        result = []
        for e in cursor:
            e['_id'] = str(e['_id'])
            result.append(e)

        return jsonify(result)
