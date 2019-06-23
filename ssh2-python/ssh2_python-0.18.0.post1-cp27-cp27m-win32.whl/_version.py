
import json

version_json = '''
{"date": "2019-06-23T12:37:26.879000", "full-revisionid": "2298fe30bc8771876f38a7cd6dc13623dd27b5be", "dirty": false, "version": "0.18.0.post1", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

