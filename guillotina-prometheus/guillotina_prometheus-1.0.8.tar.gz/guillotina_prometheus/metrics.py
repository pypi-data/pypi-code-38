from prometheus_client import Summary


request_summary = Summary('http_request', 'Time spent processing request',
                          ['method', 'view', 'response_code'])
