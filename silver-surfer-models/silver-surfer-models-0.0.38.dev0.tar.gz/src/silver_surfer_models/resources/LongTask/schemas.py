from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
)

LONG_TASK_STATES = {
    'NOT_STARTED': 'NOT_STARTED',
    'IN_PROGRESS': 'IN_PROGRESS',
    'SUCCESSFUL': 'SUCCESSFUL',
    'FAILED': 'FAILED',
}
LONG_TASK_NAMES = {
    'PROCESS_PETITION_DOC': 'PROCESS_PETITION_DOC',
}


def _validate_long_task_name(name):
    if name not in LONG_TASK_NAMES.keys():
        raise ValidationError(
            'Invalid long task name',
        )


def _validate_long_task_state(state):
    if state not in LONG_TASK_STATES.keys():
        raise ValidationError(
            'Invalid long task state',
        )


class LongTaskResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    trial_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=_validate_long_task_name)
    state = fields.String(required=True, validate=_validate_long_task_state)
    progress = fields.Float(required=True)
    celery_task_id = fields.String(required=True)
    result = fields.String()
    updated_at = fields.DateTime()


class LongTaskQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    trial_id = fields.Integer()
    name = fields.String(validate=_validate_long_task_name)
    state = fields.String(validate=_validate_long_task_state)
    celery_task_id = fields.String(validate=not_blank)


class LongTaskPatchSchema(Schema):
    state = fields.String(validate=_validate_long_task_state)
    progress = fields.Float()
    result = fields.String()
