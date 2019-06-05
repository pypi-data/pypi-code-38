from flask_restplus import Namespace, Resource, fields
from flask import request, jsonify

import time
import uuid

from strongr.core.domain.schedulerdomain import SchedulerDomain
from strongr.restdomain.api.utils import namespace_require_oauth


ns = Namespace('scheduler', description='Operations related to the schedulerdomain')

post_task = ns.model('post-task', {
    'image': fields.String(required=True, min_length=1, description='The docker image where the script is executed'),
    'script': fields.String(required=True, min_length=1, description='The shellcode to be executed'),
    'scratch': fields.String(required=True, min_length=1, description='Does the job need a scratch dir?'),
    'cores': fields.Integer(required=True, min=1, description='The amount of cores needed to peform the task'),
    'memory': fields.Integer(required=True, min=1, description="The amount of ram in GiB needed to peform the task"),
    'secrets': fields.List(fields.String, required=False, description='A list of keys of secrets to be injected into the process')
})

@ns.route('/tasks/status/<string:tasks>')
class TaskStatusQuery(Resource):
    def __init__(self, *args, **kwargs):
        super(TaskStatusQuery, self).__init__(*args, **kwargs)

    @ns.response(200, 'OK')
    #@namespace_require_oauth('task')
    def get(self, tasks):
        tasks = [x.strip() for x in tasks.split(',') if len(x.strip()) > 0] # convert to array

        if tasks is None or len(tasks) == 0:
            return None, 400

        schedulerService = SchedulerDomain.schedulerService()
        queryFactory = SchedulerDomain.queryFactory()

        query = queryFactory.newRequestJobInfo(tasks)
        result = schedulerService.getQueryBus().handle(query)

        output = {}
        for job in result:
            output[job.job_id] = {
                'state': str(job.state).split('.')[-1],
                'stdout': job.stdout
            }

        return output, 200


#@ns.route('/task/<string:task_id>')
#class GetTask(Resource):
#    def __init__(self, *args, **kwargs):
#        super(GetTask, self).__init__(*args, **kwargs)
#
#    @ns.response(200, 'OK')
#    #@namespace_require_oauth('task')
#    def get(self, task_id):
#        """Requests task status"""
#        schedulerService = SchedulerDomain.schedulerService()
#        queryFactory = SchedulerDomain.queryFactory()
#
#        query = queryFactory.newRequestScheduledJobs([task_id])
#
#        result = schedulerService.getQueryBus().handle(query)
#        return result, 200

@ns.route('/task')
class Tasks(Resource):
    def __init__(self, *args, **kwargs):
        super(Tasks, self).__init__(*args, **kwargs)

    @ns.response(201, 'Task successfully created.')
    #@namespace_require_oauth('task')
    @ns.expect(post_task, validate=True)
    def post(self):
        """Creates a new task."""
        schedulerService = SchedulerDomain.schedulerService()
        commandFactory = SchedulerDomain.commandFactory()

        image = request.json['image']
        script = request.json['script'].splitlines()
        scratch = request.json['scratch']
        cores = int(request.json['cores'])
        memory = int(request.json['memory'])
        job_id = str(int(time.time())) + '-' + str(uuid.uuid4())

        if 'secrets' in request.json:
            secrets = request.json['secrets']
        else:
            secrets = []

        command = commandFactory.newScheduleJobCommand(image, script, job_id, scratch, cores, memory, secrets)

        schedulerService.getCommandBus().handle(command)
        return {'job_id': job_id}, 201
