from functools import partial

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
)
from tracuni.schema.pipe_methods import (
    pipe_head,
    pipe_sep_string,
    ext_tracer_path,
    ext_tracer_short_path,
    ext_tracer_full_path
)
from tracuni.schema.shared_rules import rule_inner_out_tracer_context, rule_span_peer_name_from_application_name

ruleset = (
    Rule(
        description="Метод, вызвавший запрос",
        destination=Destination(DestinationSection.REUSE, 'point_name'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_short_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Путь по методам, вызвавшим запрос",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.path'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Метод, вызвавший запрос",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.method'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_full_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Задать имя участку",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'name'
        ),
        pipeline=(
            lambda x: ("app", "retry", x[0]),
            partial(pipe_sep_string, **{'sep': ('::', ' (', ')')}),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, 'point_name',
            ),
        ),
        stage=Stage.PRE,
    ),
    rule_inner_out_tracer_context,
    rule_span_peer_name_from_application_name,
)
