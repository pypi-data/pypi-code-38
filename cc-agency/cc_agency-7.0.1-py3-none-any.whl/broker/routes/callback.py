from time import time

import jsonschema
from flask import request, jsonify
from werkzeug.exceptions import Unauthorized, NotFound, BadRequest
from bson.objectid import ObjectId

from cc_core.commons.red_to_blue import convert_red_to_blue

from cc_agency.commons.schemas.callback import callback_schema
from cc_agency.commons.helper import batch_failure
from cc_agency.commons.secrets import get_batch_secret_keys
from cc_agency.commons.secrets import fill_batch_secrets


def callback_routes(app, mongo, auth, conf, controller, trustee_client):
    @app.route('/callback/<batch_id>/<token>', methods=['GET'])
    def get_callback(batch_id, token):
        if not auth.verify_callback(batch_id, token):
            raise Unauthorized()

        batch = mongo.db['batches'].find_one(
            {'_id': ObjectId(batch_id), 'state': 'processing'}
        )
        if not batch:
            raise NotFound('Object not found.')

        batch_secret_keys = get_batch_secret_keys(batch)
        response = trustee_client.collect(batch_secret_keys)

        if response['state'] == 'failed':
            debug_info = 'Trustee service failed:\n{}'.format(response['debug_info'])
            disable_retry = response.get('disable_retry')
            batch_failure(mongo, batch_id, debug_info, None, conf, disable_retry_if_failed=disable_retry)
            raise NotFound(debug_info)

        batch_secrets = response['secrets']
        batch = fill_batch_secrets(batch, batch_secrets)

        experiment_id = batch['experimentId']

        experiment = mongo.db['experiments'].find_one(
            {'_id': ObjectId(experiment_id)}
        )

        red_data = {
            'redVersion': experiment['redVersion'],
            'cli': experiment['cli'],
            'inputs': batch['inputs'],
            'outputs': batch['outputs']
        }

        blue_batches = convert_red_to_blue(red_data)

        return jsonify(blue_batches[0])

    @app.route('/callback/<batch_id>/<token>', methods=['POST'])
    def post_callback(batch_id, token):
        if not auth.verify_callback(batch_id, token):
            raise Unauthorized()

        try:
            bson_id = ObjectId(batch_id)
        except Exception:
            raise BadRequest('Not a valid BSON ObjectId.')

        batch = mongo.db['batches'].find_one(
            {'_id': bson_id, 'state': 'processing'},
            {'attempts': 1, 'node': 1}
        )
        if not batch:
            raise NotFound('Object not found.')

        if not request.json:
            debug_info = 'Callback did not send CC-Agent data as JSON.'
            batch_failure(mongo, batch_id, debug_info, None, conf)
            raise BadRequest(debug_info)

        data = request.json

        try:
            jsonschema.validate(data, callback_schema)
        except Exception:
            debug_info = 'CC-Agent data sent by callback does not comply with jsonschema.'
            batch_failure(mongo, batch_id, debug_info, data, conf)
            raise BadRequest(debug_info)

        if data['state'] == 'failed':
            debug_info = 'Callback sent state "failed".'
            batch_failure(mongo, batch_id, debug_info, data, conf)

            return '', 200

        mongo.db['batches'].update(
            {'_id': bson_id},
            {
                '$set': {
                    'state': 'succeeded'
                },
                '$push': {
                    'history': {
                        'state': 'succeeded',
                        'time': time(),
                        'debugInfo': None,
                        'node': batch['node'],
                        'ccagent': data
                    }
                }
            }
        )

        controller.send_json({'destination': 'scheduler'})

        return '', 200
