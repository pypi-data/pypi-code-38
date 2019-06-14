import json
from textwrap import dedent as ____
from tracuni.define.type import PipeCommand
import logging


def debug_output(point_context, debug_info):
    try:
        point_name = point_context.point_ref.__qualname__
        # noinspection PyProtectedMember
        adapter_config = json.dumps(point_context.adapter.config._asdict(), indent=2)
        variant = point_context.engine.schema_feed.variant
        schema = json.dumps(dict(
            (k.name, "{}::{}".format(rule.destination.section.name, rule.destination.name))
            for k, v in point_context.engine.extractors.items()
            for rule in v
        ))
        value = debug_info.get('value')
        if not value:
            return
        processor_idx = debug_info['processor_idx']
        extractor = debug_info['extractor']
        extractor_description = extractor.description
        processor = debug_info['processor']
        if processor_idx > 0:
            processor = extractor.pipeline[processor_idx - 1]
            if processor_idx >  1 and processor == PipeCommand.TEE:
                processor = extractor.pipeline[processor_idx - 2]
        processor_name = processor.__name__

        output = ____(f"""


        Calling app method <<{point_name}>> marked as: <<{variant}>>,
        processing with <<{processor_name}>> method from rule described as: <<{extractor_description}>>
        
        Values received:
        ================
        {value}
        ================
        """)

        logging.info(output)
        return output

    except Exception as exc:
        logging.debug("Pipeline debug ruined itself")
        logging.exception(exc)
