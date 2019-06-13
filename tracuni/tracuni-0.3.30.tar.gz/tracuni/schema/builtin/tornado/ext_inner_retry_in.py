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
)
from tracuni.schema.shared_rules import (
    rule_inner_in_tracer_context,
    rule_span_peer_name_from_application_name,
)

ruleset = (
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
                OriginSection.POINT_ARGS, 'retries',
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Занести максимальное количество попыток в теги",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'app.retries.max'
        ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS, 'retries',
            ),
        ),
        stage=Stage.PRE,
    ),
    rule_inner_in_tracer_context,
    rule_span_peer_name_from_application_name,
)
