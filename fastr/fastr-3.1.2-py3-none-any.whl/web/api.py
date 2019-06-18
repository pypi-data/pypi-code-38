import datetime
import functools
import multiprocessing
import threading

from flask import url_for, abort
from flask_restplus import Api, Resource, reqparse, fields

from . import app
from ..helpers import config, log

api = Api(app,
          doc='/api/doc/',
          version='0.1',
          title='Fastr REST API',
          description='A REST API to interact with Fastr via the web',
          default_mediatype='application/json')

runs = {}


STATUS_MANAGER = multiprocessing.Manager()


def update_status(job, job_status):
    job_status[job.id] = str(job.status), str(job.node_id)


def update_job_result(job, job_status, job_results):
    job_results[job.id] = str(job.output_data)


def network_lock_thread(lock, network):
    log.debug('WAITING FOR LOCK')
    with lock:
        log.debug('CALLING NETWORK ABORT')
        network.abort()


def network_runner(network, source_data, sink_data, chuck_status, job_status, job_results, abort_lock):
    network.job_finished_callback = functools.partial(update_job_result, job_status=job_status, job_results=job_results)
    network.job_status_callback = functools.partial(update_status, job_status=job_status)
    abort_lock.acquire()
    abort_thread = threading.Thread(name="NetworkAbort", target=network_lock_thread, args=(abort_lock, network))
    abort_thread.start()

    network.execute(source_data, sink_data)


class Run(object):
    def __init__(self, id_, network, source_data, sink_data):
        self.id = id_
        self.chunks = STATUS_MANAGER.list()
        self.jobs = STATUS_MANAGER.dict()
        self.job_results = STATUS_MANAGER.dict()
        self.source_data = source_data
        self.sink_data = sink_data
        self.network = network.id
        self.abort_lock = multiprocessing.Lock()
        self.process = self.run_network(network, source_data, sink_data, self.abort_lock)

    def run_network(self, network, source_data, sink_data, abort_lock):
        process = multiprocessing.Process(target=network_runner,
                                          args=(network,
                                                source_data,
                                                sink_data,
                                                self.chunks,
                                                self.jobs,
                                                self.job_results,
                                                abort_lock),
                                          name=self.id)
        process.start()
        return process

    def status(self):
        return {'job_status': dict(self.jobs),
                'job_results': dict(self.job_results)}

    def abort(self):
        log.debug('RELEASING ABORT LOCK')
        self.abort_lock.release()

        if self.process:
            log.debug('JOINING PROCESS')
            self.process.join(timeout=3)

            if self.process.is_alive():
                log.debug('TERMINATING PROCESS')
                self.process.terminate()


class ObjectUrl(fields.Raw):
    __schema_type__ = "string"

    def __init__(self, object_classs, **kwargs):
        super(ObjectUrl, self).__init__(**kwargs)
        self._object_class = object_classs

    def format(self, value):
        if isinstance(self._object_class, str):
            return url_for(self._object_class, id=value)
        else:
            return api.url_for(self._object_class, id=value)


class SubUrl(fields.Raw):
    __schema_type__ = "string"

    def __init__(self, object_classs, subfield, **kwargs):
        super(SubUrl, self).__init__(**kwargs)
        self._object_class = object_classs
        self._subfield = subfield

    def format(self, value):
        if isinstance(self._object_class, str):
            url = url_for(self._object_class, id=value)
        else:
            url = api.url_for(self._object_class, id=value)

        return '{}/{}'.format(url, self._subfield)


class ToolApi(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Tool not found')
    def get(self, id_, version=None):
        """
        Get a Tool json description from the server
        """
        try:
            return tools[id_, version].dumps(method='json')
        except KeyError:
            abort(404)


tool_list_model = api.model('ToolList', {
    'tools': fields.List(fields.String),
})


class ToolListApi(Resource):
    @api.marshal_with(tool_list_model)
    def get(self):
        """
        Get a list of all Tools known to the server
        """
        data = {'tools': [url_for('api_version_tool', id=x.ns_id, version=x.command_version) for x in tools.values()]}
        print('Data {}'.format(data))
        return data


class NetworkApi(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Network not found')
    def get(self, id_):
        """
        Get a Network json description from the server
        """
        try:
            return networklist[id_].dumps(method='dict')
        except KeyError:
            abort(404)


network_list_model = api.model('NetworkList', {
    'networks': fields.List(ObjectUrl('api_network', attribute='id'))
})


class NetworkListApi(Resource):
    @api.marshal_with(network_list_model)
    def get(self):
        """
        Get a list of the networks
        """
        data = {'networks': list(networklist.values())}
        print('Data: {}'.format(data))
        return data


run_model = api.model('Run', {
    'url': fields.Url,
    'network': ObjectUrl('api_network', attribute='network'),
    'status': ObjectUrl('api_status', attribute='id'),
    'source_data': fields.Raw,
    'sink_data': fields.Raw,
})


class RunApi(Resource):
    """
    Run API documentation
    """
    @api.response(200, 'Success')
    @api.response(404, 'Network not found')
    @api.marshal_with(run_model)
    def get(self, id_):
        """
        Get information about a Network run
        """
        try:
            return runs[id_]
        except KeyError:
            abort(404)

    @api.response(204, 'Aborted Network run')
    @api.response(404, 'Network not found')
    def delete(self, id_):
        """
        Abort a Network run and stop all associated execution
        """
        if id_ in runs:
            runs[id_].abort()
            return None, 204
        else:
            return None, 404


run_list_model = api.model("RunList", {
    'runs': fields.List(ObjectUrl('api_run', attribute='id'))
})


class RunListApi(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('network', type=str, required=True, location='json',
                                help='No network id specified')
    request_parser.add_argument('source_data', type=dict, required=True, location='json',
                                help='No source data was supplied')
    request_parser.add_argument('sink_data', type=dict, required=True, location='json',
                                help='No sink data was supplied')

    @api.marshal_with(run_list_model)
    def get(self):
        """
        Get a list of all Network runs on the server
        """
        return {'runs': list(runs.values())}

    @api.expect(request_parser)
    @api.response(201, "Created Network run")
    def post(self):
        """
        Create a new Network run and start execution
        """
        args = self.request_parser.parse_args()

        network = networklist[args['network']]
        run_id = '{}_{}'.format(network.id, datetime.datetime.now().isoformat())
        runs[run_id] = Run(run_id, network, args['source_data'], args['sink_data'])

        return {'run_id': run_id,
                'run': url_for('api_run', id=run_id, _external=True),
                'status': url_for('api_status', id=run_id, _external=True)}, 201, {'Location': url_for('api_run', id=run_id)}


class StatusApi(Resource):
    @api.response(200, "Success")
    @api.response(404, "Run not found")
    def get(self, id_):
        """
        Get the status of a Network Run on the server
        """
        try:
            return runs[id_].status()
        except KeyError:
            abort(404)


api.add_resource(NetworkApi, '/api/networks/<id>', endpoint='api_network')
api.add_resource(NetworkListApi, '/api/networks', endpoint='api_networks')
api.add_resource(ToolApi, '/api/tools/<id>', endpoint='api_tool')
api.add_resource(ToolApi, '/api/tools/<id>/<version>', endpoint='api_version_tool')
api.add_resource(ToolListApi, '/api/tools', endpoint='api_tools')
api.add_resource(RunApi, '/api/runs/<id>', endpoint='api_run')
api.add_resource(RunListApi, '/api/runs', endpoint='api_runs')
api.add_resource(StatusApi, '/api/runs/<id>/status', endpoint='api_status')

