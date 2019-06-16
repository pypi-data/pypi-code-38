# test_capitalize.py
import pytest

from bamboo_lib.models import PipelineStep, ComplexPipelineExecutor, AdvancedPipelineExecutor
from bamboo_lib.steps import LoadStep, DownloadStep

def build_pipeline(pipeline_kind=ComplexPipelineExecutor, complexity="advanced"):

    class Nest1Step(PipelineStep):
        def run_step(self, prev_result, params):
            print("-----Nest1Step-----")
            for item in [3, 5]:
                yield item

    class Nest2Step(PipelineStep):
        def run_step(self, prev_result, params):
            print("-----Nest2Step-----")
            for item in [prev_result * 4, prev_result * 6]:
                yield item

    class DisplayStep(PipelineStep):
        def run_step(self, prev_result, params):
            print("RESULT!!", prev_result, "\n")
            return prev_result

    class DummyStepSimple(PipelineStep):
        def run_step(self, prev_result, params):
            print("-----START-----")
            return "Gamma"

    class DummyStep(PipelineStep):
        def run_step(self, prev_result, params):
            print("-----START-----")
            for item in ["Alpha", "Beta", "Gamma"]:
                yield item

    class TransformStep(PipelineStep):
        def run_step(self, prev_result, params):
            print("Check 1:", prev_result)
            return prev_result + "ADDED"

    class GenerateSchemaStep(PipelineStep):
        def run_step(self, prev_result, params):
            # this should return a df reflecting the changes in the previous step,
            # but instead it returns the initial version of the dataframe object without any changes
            title = prev_result
            print("Check 2: (Should be +ADDED)", title)
            print("----END----")
            return title

    transform_step = TransformStep()
    generate_schema_step = GenerateSchemaStep()
    pp = pipeline_kind({})
    if complexity == "advanced":
        dummy_step = DummyStep()
        pp = pp.foreach(dummy_step).next(transform_step).next(generate_schema_step).endeach()
    elif complexity == "nested":
        nest_1_step = Nest1Step()
        nest_2_step = Nest2Step()
        display_step = DisplayStep()
        pp = pp.foreach(nest_1_step).foreach(nest_2_step).next(display_step).endeach().endeach()
    else:
        dummy_step_simple = DummyStepSimple()
        pp = pp.next(dummy_step_simple).next(transform_step).next(generate_schema_step)

    return pp


def test_complex_pipeline():
    pipeline = build_pipeline(ComplexPipelineExecutor)
    res = pipeline.run_pipeline()
    assert res == "GammaADDED"


def test_complex_pipeline_with_nested_loops():
    pipeline = build_pipeline(ComplexPipelineExecutor, complexity="nested")
    assert isinstance(pipeline, ComplexPipelineExecutor)
    res = pipeline.run_pipeline()
    assert res == 30


def test_advanced_pipeline_without_loops():
    pipeline = build_pipeline(AdvancedPipelineExecutor, complexity="simple")
    res = pipeline.run_pipeline()
    assert res == "GammaADDED"


def test_advanced_pipeline_with_loops():
    pipeline = build_pipeline(AdvancedPipelineExecutor, complexity="advanced")
    res = pipeline.run_pipeline()
    assert res == "GammaADDED"


def test_advanced_pipeline_with_nested_loops():
    pipeline = build_pipeline(AdvancedPipelineExecutor, complexity="nested")
    res = pipeline.run_pipeline()
    assert res == 30

def test_create_load_step_with_nullable_list():
    load_step = LoadStep("bls_test_import", None, if_exists="append", pk=["year"], nullable_list=["alpha"])
    assert load_step

def test_callback_in_dl_step():
    def my_callback_fun(x):
        return "This is it."
    dl_step = DownloadStep(connector="http-local", connector_path=__file__, callback=my_callback_fun)
    res = dl_step.connector.download(callback=my_callback_fun, force=True)
    with open(res, 'r') as my_file:
        assert my_file.read() == "This is it."

def test_no_callback_in_dl_step():
    dl_step = DownloadStep(connector="http-local", connector_path=__file__)
    res = dl_step.connector.download(force=True)
    with open(res, 'r') as my_file:
        assert '''"title": "delectus aut autem"''' in my_file.read()
