
import json

version_json = '''
{"date": "2019-06-23T13:10:38.777213", "dirty": false, "error": null, "full-revisionid": "2298fe30bc8771876f38a7cd6dc13623dd27b5be", "version": "0.18.0.post1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

