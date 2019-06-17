# from functools import partial
# from ..config import WebConfig
#
#
# def api_root(ip, port):
#     return f"http://{ip}:{port}/"
#
#
# def _req_url(ip, port, name):
#     return api_root(ip, port) + str(name)
#
#
# task_req_url = partial(_req_url, WebConfig.POSTGREST_IP, WebConfig.POSTGREST_PORT)
