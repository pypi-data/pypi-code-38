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
)
from tracuni.schema.shared_rules import rule_amqp_out_tracer_context, rule_span_peer_name_from_application_name

ruleset = (
    rule_amqp_out_tracer_context,
    Rule(
        description="Наименование участка повторного запуска задачи",
        destination=Destination(DestinationSection.SPAN_NAME, 'name'),
        pipeline=(lambda _: 'amqp::retry',),
        origins=(Origin(OriginSection.ADAPTER, None),),
        stage=Stage.PRE,
    ),
    rule_span_peer_name_from_application_name,
    Rule(
        description="Вывести повторы задачи в теги",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.retry'),
        pipeline=(
            lambda task_data: f"{task_data[0]}/{task_data[1]}"
            if task_data else None,
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS, "retry",
            ),
            Origin(
                OriginSection.POINT_ARGS, "retry_count",
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести идентификатор задачи в теги",
        destination=Destination(DestinationSection.SPAN_TAGS, 'app.task'),
        pipeline=(
            pipe_head,
            lambda tid: f"#{tid}" if tid else None,
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS, "tid",
            ),
        ),
        stage=Stage.PRE,
    ),
)
