from flask import jsonify, request
from werkzeug.exceptions import Unauthorized
from bson.objectid import ObjectId


def _get_node_gpu_info(conf_nodes, node_name):
    node = conf_nodes.get(node_name)
    if node:
        hardware = node.get('hardware')
        if hardware:
            gpus = hardware.get('gpus')
            if gpus:
                return gpus
    return None


def nodes_routes(app, mongo, auth, conf):
    @app.route('/nodes', methods=['GET'])
    def get_nodes():
        conf_nodes = conf.d['controller']['docker']['nodes']
        user = auth.verify_user(request.authorization)
        if not user:
            raise Unauthorized()

        cursor = mongo.db['nodes'].find()

        nodes = list(cursor)
        node_names = [node['nodeName'] for node in nodes]

        cursor = mongo.db['batches'].find(
            {
                'node': {'$in': node_names},
                'state': {'$in': ['scheduled', 'processing']}
            },
            {'experimentId': 1, 'node': 1}
        )
        batches = list(cursor)
        experiment_ids = list(set([ObjectId(b['experimentId']) for b in batches]))

        cursor = mongo.db['experiments'].find(
            {'_id': {'$in': experiment_ids}},
            {'container.settings.ram': 1}
        )
        experiments = {str(e['_id']): e for e in cursor}

        for node in nodes:
            batches_ram = [
                {
                    'batchId': str(b['_id']),
                    'ram': experiments[b['experimentId']]['container']['settings']['ram']
                }
                for b in batches
                if b['node'] == node['nodeName']
            ]
            node['currentBatches'] = batches_ram
            gpu_info = _get_node_gpu_info(conf_nodes, node['nodeName'])
            if gpu_info:
                node['gpus'] = gpu_info
            del node['_id']

        return jsonify(nodes)
