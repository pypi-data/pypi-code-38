import datetime
import json
from marshmallow import Schema, fields, validates, ValidationError
from potnanny_core.schemas.outlet import GenericOutletSchema

class ScheduleOnOffSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    room_id = fields.Integer(required=True)
    is_active = fields.Boolean(required=True)
    created = fields.DateTime(dump_only=True)
    outlet = fields.Method("validate_outlet")
    days = fields.Integer(required=True)
    on_utc_hour = fields.Integer(required=True)
    on_minute = fields.Integer(required=True)
    off_utc_hour = fields.Integer(required=True)
    off_minute = fields.Integer(required=True)

    @validates('days')
    def validate_days(self, value):
        if value < 0 or value > 127:
            raise ValidationError('Value must be from 0 to 127')

    @validates('on_utc_hour')
    @validates('off_utc_hour')
    def validate_hour(self, value):
        if value < 0 or value > 23:
            raise ValidationError('Value must be from 0 to 23')

    @validates('on_minute')
    @validates('off_minute')
    def validate_minute(self, value):
        if value < 0 or value > 59:
            raise ValidationError('Value must be from 0 to 59')

    def validate_outlet(self, obj):
        working_item = None

        if type(obj) is dict:
            # a dict. good. super easy to deal with
            working_item = obj
        else:
            # ug. an unknown object. create a dict from it.
            working_item = {k: v for k,v in obj.__dict__.items() if not k.startswith('_')}

        if 'outlet' not in working_item:
            raise ValidationError("No outlet data defined.")

        if type(working_item['outlet']) is str:
            outlet = json.loads(working_item['outlet'])
        else:
            outlet = working_item['outlet']

        data, errors = GenericOutletSchema(exclude=['state']).dump(outlet)
        if errors:
            print("ERROR")
            print(errors)
            raise ValidationError(errors)

        return json.dumps(data)


class RoomLightManagerSchema(Schema):
    class META:
        strict = True

    room_id = fields.Integer(
                required=True,
                error_messages={'required': 'room_id is required'})
    schedules = fields.Nested('ScheduleOnOffSchema',
                    exclude=['room_id'], many=True)
    active_schedule = fields.Nested('ScheduleOnOffSchema',
                    exclude=['room_id'], dump_only=True)
    current_phase = fields.Str(dump_only=True)
