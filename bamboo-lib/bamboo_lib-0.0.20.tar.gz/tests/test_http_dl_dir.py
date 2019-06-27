# test_capitalize.py
import pytest
import os
from bamboo_lib.models import PipelineStep, AdvancedPipelineExecutor
from bamboo_lib.helpers import grab_connector



class DisplayStep(PipelineStep):
    def run_step(self, prev_result, params):
        print("RESULT:", prev_result, "\n")
        return prev_result

class DownloadStep(PipelineStep):
    def run_step(self, prev, params):
        # Download Cube (URL defined in conns.yaml file.)
        # This step will save the contents of the connector target
        # to a file and then pass a file path to the next step
        return self.connector.download(params=params)


@pytest.fixture()
def pipeline():
    source_connector = grab_connector(__file__, "http-local")
    http_dl_step = DownloadStep(connector=source_connector)
    show_step = DisplayStep()
    pp = AdvancedPipelineExecutor({})
    pp = pp.next(http_dl_step).next(show_step)
    return pp


def test_dl_default_path(pipeline):
    res = pipeline.run_pipeline()
    assert res == "/tmp/999f2fa455aff231b7daa3680efdb03abd078fa1b009e38677c42d24"

def test_dl_custom_path1(pipeline):
    os.environ["BAMBOO_DOWNLOAD_FOLDER"] = "/tmp/a2/"
    res = pipeline.run_pipeline()
    assert res == "/tmp/a2/999f2fa455aff231b7daa3680efdb03abd078fa1b009e38677c42d24"
    del os.environ["BAMBOO_DOWNLOAD_FOLDER"]

def test_dl_custom_path2(pipeline):
    os.environ["BAMBOO_DOWNLOAD_FOLDER"] = "/tmp/a2"
    res = pipeline.run_pipeline()
    assert res == "/tmp/a2/999f2fa455aff231b7daa3680efdb03abd078fa1b009e38677c42d24"
    del os.environ["BAMBOO_DOWNLOAD_FOLDER"]
