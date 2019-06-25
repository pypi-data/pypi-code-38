import logging

from flask import request, jsonify
from munch import Munch

from . import remote
from schedule import TriggerActor

log = logging.getLogger('Ficus')

@remote.route('/remote/ta-service/<int:jobId>', methods=['DELETE'])
def stop_job(jobId):
    return TriggerActor.stop_job(jobId)

@remote.route('/remote/ta-service/<int:jobId>/<int:logId>', methods=['DELETE'])
def stop_task(jobId,logId):
    is_executing = request.args.get("isExecuting",default="false")
    return TriggerActor.stop_task(jobId,logId,'true'==is_executing)

@remote.route('/remote/ta-service', methods=['POST'])
def handle_trigger():
    taskParam = request.json
    body = Munch(taskParam)
    log.debug(f"触发了一次请求:{taskParam}")
    """
    {
  "actorBlockStrategy": "SERIAL_EXECUTION",
  "actorHandler": "multipleArticleMessageCEHandler",
  "actorParams": {
    "code_": "locus.multiple.article.message.ce-0",
    "projectCode_": "LOCUS",
    "site_": "S1"
  },
  "jobId": 20081,
  "jobType": "BEAN",
  "limitTimes": -1,
  "logId": 55,
  "scriptJobRemark": "None",
  "scriptJobSource": "None",
  "updateTime": "2018-02-04 10:35:39"
}
    """

    return TriggerActor.handle_trigger(body).to_json()


@remote.route('/remote/ta-service/ping', methods=['GET'])
def ping():
    return jsonify("pong")

@remote.route('/remote/ta-service/idle/<int:job_id>', methods=['GET'])
def idle(job_id:int):
    return jsonify(TriggerActor.idle(job_id))