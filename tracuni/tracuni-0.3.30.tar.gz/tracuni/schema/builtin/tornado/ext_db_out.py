from functools import partial

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
    PipeCommand,
)
from tracuni.schema.pipe_methods import (
    ext_sql_args,
    ext_tracer_out_point,
    ext_tracer_path,
    ext_tracer_full_path,
    pipe_head,
    pipe_sep_string,
    pipe_db_service_name_from_config,
    pipe_catch_essential,
    pipe_mask_secret_catch_essentials,
    pipe_dump,
    pipe_cut,
    ext_api_kind,
    ext_sql_response,
)


ruleset = (
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
            lambda x: ('db', *x),
            partial(pipe_sep_string, **{'sep': ("::", " (", ")")}),
        ),
        origins=(
            Origin(
                OriginSection.CALL_STACK,
                partial(ext_tracer_out_point, **{'shift': 0}),
            ),
            Origin(
                OriginSection.CALL_STACK,
                ext_tracer_out_point,
            ),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Наименование партнерского сервиса сохранить для "
                    "переиспользования",
        destination=Destination(
            DestinationSection.REUSE,
            'peer_name',
          ),
        pipeline=(
            pipe_head,
            pipe_db_service_name_from_config,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, 'self'),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Наименование партнерского сервиса записать в участок",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'remote_endpoint',
          ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'peer_name'),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести праметры SQL запроса в аннотации",
        destination=Destination(DestinationSection.SPAN_LOGS, 'SQL_params'),
        pipeline=(
            pipe_head,
            # pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS,
                ext_sql_args,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести ответ сервера SQL",
        destination=Destination(DestinationSection.SPAN_LOGS, 'SQL_response'),
        pipeline=(
            pipe_head,
            # pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret_catch_essentials,
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.POINT_RESULT,
                ext_sql_response,
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Запомнить ошибку для вывода",
        destination=Destination(DestinationSection.REUSE, 'error'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.SPAN, 'error'),
        ),
        stage=Stage.POST,
    ),
)
