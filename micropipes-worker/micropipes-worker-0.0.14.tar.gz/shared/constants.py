

MQ_COORDINATOR_EXCHANGE = 'coordinator'
MQ_COORDINATOR_EXCHANGE_TYPE = 'topic'
MQ_COORDINATOR_QUEUE = 'micropipes.coordinator'

MQ_WORKER_REGISTER = 'worker.register'
MQ_WORKER_REGISTERED_ID = 'worker.registered_id'
MQ_WORKER_UNREGISTER = 'worker.unregister'
MQ_WORKER_READY_FOR_JOB_START = 'worker.ready4jobstart'
MQ_WORKER_HEARTBEAT = 'worker.hearbeat'
MQ_WORKER_UNREGISTERED = 'worker.unregistered'
MQ_JOB_FINISH_REQUEST = 'job.finish_request'
MQ_JOB_CANCEL_REQUEST = 'job.cancel_request'
MQ_JOB_START_REQUEST = 'job.start_request'
MQ_JOB_STOP_REQUEST = 'job.stop_request'
MQ_JOB_SUBMIT_REQUEST = 'job.submit.request'
MQ_JOB_SUBMIT_REQUESTED_ID = 'job.submit.requested_id'
MQ_COORDINATOR_BINDINGS = [MQ_WORKER_REGISTER, MQ_WORKER_UNREGISTER , MQ_JOB_FINISH_REQUEST , MQ_JOB_START_REQUEST ,
                           MQ_JOB_CANCEL_REQUEST, MQ_WORKER_READY_FOR_JOB_START, MQ_JOB_SUBMIT_REQUEST,
                           MQ_WORKER_HEARTBEAT, MQ_JOB_STOP_REQUEST]

MQ_JOB_ASSIGN = 'job.assign'
MQ_JOB_UNASSIGN = 'job.unassign'
MQ_JOB_STATUS = 'job.status'
MQ_COORDINATOR_WORKER_BINDINGS = [MQ_JOB_ASSIGN, MQ_JOB_UNASSIGN, MQ_JOB_STATUS ]

JOB_STATUS_WAIT = 'status.wait'
JOB_STATUS_STARTED = 'status.started'
JOB_STATUS_FINISHED = 'status.finished'
JOB_STATUS_CANCELED = 'status.canceled'
JOB_STATUS_STOP = 'status.stop'

WORKER_STATUS_UNKNOWN = 'status.unknown'
WORKER_STATUS_REGISTERED = 'status.registered'

JOB_START_DATA = 'job.start.data'
JOB_FINISH_DATA = 'job.finish.data'

MQ_DATA_EXCHANGE = 'data'
MQ_DATA_EXCHANGE_TYPE = 'topic'

HEARTBEAT_CHECK_INTERVAL = 5
HEARTBEAT_DIFF = 30.0
HEARTBEAT_SEND_INTERVAL = HEARTBEAT_DIFF/2
