# -*- coding: utf-8 -*-

import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions


def run(lambda_class,
        input_subscription,
        output_topic,
        argv=None):
    """Build and run the pipeline."""
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    pipeline_options.view_as(StandardOptions).streaming = True
    p = beam.Pipeline(options=pipeline_options)

    messages = p | beam.io.ReadFromPubSub(subscription=input_subscription)
    messages | beam.ParDo(lambda_class) | beam.io.WriteToPubSub(output_topic)
    result = p.run()
    result.wait_until_finish()
