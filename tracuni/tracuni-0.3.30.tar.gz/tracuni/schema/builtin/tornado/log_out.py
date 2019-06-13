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
from tracuni.misc.helper import json_dumps_decode
from tracuni.schema.shared_rules import rule_inner_out_tracer_context, rule_span_peer_name_from_application_name

def serialize_point_args(x):
    try:
        x = json_dumps_decode(x[0]._asdict()) if x else None
    except Exception as exc:
        return str(exc)
    return x

ruleset = (
    Rule(
        description="Путь по методам, вызвавшим запрос",
        destination=Destination(DestinationSection.REUSE, 'point_path'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.CALL_STACK, ext_tracer_path),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Путь по методам, вызвавшим запрос в теги",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.path'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'point_path'),
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
            lambda x: ("app", "log", x[0]),
            partial(pipe_sep_string, **{'sep': ('::', ' (', ')')}),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, 'point_path',
            ),
        ),
        stage=Stage.PRE,
    ),
    rule_span_peer_name_from_application_name,
    Rule(
        description="Вывод аргументов",
        destination=Destination(DestinationSection.SPAN_LOGS, 'args'),
        pipeline=(
            serialize_point_args,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, None),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Разделитель запроса и ответа",
        destination=Destination(
            DestinationSection.SPAN_LOGS,
            'divider',
        ),
        pipeline=(
            lambda _: "--------------------------------",
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                None,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывод результата",
        destination=Destination(DestinationSection.SPAN_LOGS, 'res'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_RESULT, None),
        ),
        stage=Stage.POST,
    ),
)
