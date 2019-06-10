import os


# note: the logger is writing to stack driver -> we read from stack driver
# stackdriver -> pubsub (google service) -> fluentd from pubsub
def add_backend_specific_logs(logging_values):
    if os.environ.get('SYSTEM_APP') == "rookout_backend":
        import flask
        if flask.has_request_context():
            request_url, request_id, agentId = flask.request.url, flask.request.headers.get("RUID"), flask.request.headers.get("X-Agent-ID")
            logging_values["requestUrl"] = request_url
            logging_values["requestId"] = request_id
            logging_values["agentId"] = agentId
            logging_values["requestRemoteIp"] = flask.request.remote_addr
