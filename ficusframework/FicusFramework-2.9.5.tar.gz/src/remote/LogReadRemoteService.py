# 日志获取的远程接口
from datetime import datetime

from schedule.utils.log import TaskLogFileAppender
from . import remote
from flask import request, jsonify

@remote.route('/remote/log-read-service/<string:log_id>/<int:trigger_time>', methods=['GET'])
def log_detail(trigger_time, log_id):
    from_line_num = int(request.args.get("fromLineNum", default=0))
    to_line_num = int(request.args.get("toLineNum", default=-1))
    instance_address = request.args.get("instanceAddress",default=None)
    # 获取日志文件
    return jsonify(TaskLogFileAppender.read_log(instance_address,datetime.fromtimestamp(trigger_time/1000),log_id,from_line_num,to_line_num))

@remote.route('/remote/log-read-service/tailable', methods=['GET'])
def tailable():
    """
    python的因为开启websocket或者sse非常的困难,因此暂时不支持实时的日志输出
    :return:
    """
    return jsonify(False)