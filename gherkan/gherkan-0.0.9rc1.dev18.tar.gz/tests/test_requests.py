import requests

"""Testing REST API

url - 

"""

address = '127.0.0.1'
port = 5000

simple_endpoints = ['signal_map', 'signal_map/cz', 'signal_map/en', 'actions']

complex_endpoints = ['nltext', 'signals']
complex_endpoint_requests = [
    ''
]

for endpoint in simple_endpoints:
    print("----------------------------------->")
    print(f"Testing simple GET request to endpoint '{endpoint}'")
    response = requests.get(f"http://{address}:{port}/{endpoint}").json()
    print(response)
    print("<-----------------------------------")

for endpoint, request in zip(complex_endpoints, complex_endpoint_requests):
    print("----------------------------------->")
    print(f"Testing request to endpoint '{endpoint}'")
    response = requests.get(f"http://{address}:{port}/{endpoint}").json()
    print(response)
    print("<-----------------------------------")
