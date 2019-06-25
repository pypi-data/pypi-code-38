from flask import jsonify

from . import remote


@remote.route('/actuator/info', methods=['GET'])
def actuator_info():
    return jsonify({"build":{"version":"2.9.4","artifact":"sobeycube-ficus-framework-4-py","name":"FicusFramework","group":"com.sobey.jcg"}})


@remote.route('/actuator/health', methods=['GET'])
def actuator_health():
    return jsonify({"status": "UP"})
