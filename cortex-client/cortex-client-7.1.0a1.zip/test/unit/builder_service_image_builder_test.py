import os
import json
from urllib.parse import urljoin

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex.builder.docker_image_builder import BuilderServiceImageBuilder

BASE_IMAGE = 'c12e/cortex-python36:7552534'
CORTEX_SDK_VERSION = '6.4.0'
SOURCE_ARCHIVE = None


def test_create_build_context():
    b = BuilderServiceImageBuilder(builder_url='http://foo.com', token='123')

    source = """
    def foo(params):
        print(params)
    """
    func_name = 'foofunc'
    global_code = """"""
    requirements = ['requests']
    conda_requirements = []
    d = b.create_build_context('function', source, func_name, global_code, CORTEX_SDK_VERSION, SOURCE_ARCHIVE, BASE_IMAGE, requirements, conda_requirements)
    for root, dirs, files in os.walk(d):
        assert set(['Dockerfile', 'action.py', 'conda_requirements.txt', 'requirements.txt']) == set(files)
        assert dirs == []

@mocketize
def test__build_and_push():
    b = BuilderServiceImageBuilder(builder_url='http://foo.com', token='123')

    url = 'http://foo.com/v1/builder/action'
    body = {'job': 'somejobid'}
    Entry.single_register('POST', url, status=200, body=json.dumps(body))

    build_dir = '.cortex/.builder/foo'
    image_tag = 'private-registry.cortex-dev.insights.ai/foo/bar:latest'
    r = b._build_and_push(build_dir, image_tag)

    assert r == body

@mocketize
def test__get_job():
    b = BuilderServiceImageBuilder(builder_url='http://foo.com', token='123')

    url = 'http://foo.com/v1/builder/action/123'
    body = {'status': {'succeeded': 1}}
    jobid = '123'
    Entry.single_register('GET', url, status=200, body=json.dumps(body))

    def result_predicate(v):
            is_succeeded = v.get('status', {}).get('succeeded')
            return not is_succeeded

    r = b._get_job(jobid)
    assert r == body

    r = b._wait_for_status(jobid, result_predicate)
    assert r == body