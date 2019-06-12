from marshmallow import Schema, fields, validates, ValidationError, pre_load, post_load


class GenericOutletSchema(Schema):
    class META:
        strict = True

    id = fields.Str()
    name = fields.Str(load_from='deviceName')
    type = fields.Str()
    state = fields.Method("calc_outlet_state")

    @pre_load
    def convert_id(self, item):
        if type(item) is dict:
            if type(item['id']) is int:
                item['id'] = str(int['id'])

            return item
        else:
            new_item = {k: v for k,v in item.__dict__.items() if not k.startswith('_')}
            if type(new_item['id']) is int:
                new_item['id'] = str(new_item['id'])

            return new_item

    def calc_outlet_state(self, obj):
        """
        Check for state of outlet. If unknown, returns 0|False (off)

        args:

        returns:
            boolean (True|False|1|0)
        """
        if 'relay' in obj:
            if obj['relay'] == 'open':
                return 1
            else:
                return 0
        elif 'state' in obj:
            if obj['state'] == True:
                return 1
            else:
                return 0
        else:
            return 0


    @validates('type')
    def validate_type(self, value):
        allowed = ['wireless', 'wifi-switch', 'vesync']
        if value not in allowed:
            raise ValidationError(
                "outlet type must be one of [{}]".format(",".join(allowed)))


class OutletSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(dump_only=True)
    on_code = fields.Str(required=True)
    off_code = fields.Str(required=True)
    state = fields.Boolean(dump_only=True)
    created = fields.DateTime(dump_only=True)


class VesyncOutletSchema(Schema):
    class META:
        strict = True

    id = fields.String(dump_only=True)
    name = fields.Str(required=True, load_from='deviceName')
    type = fields.Str(dump_only=True)
    relay = fields.Str()
    status = fields.Str(dump_only=True)
    state = fields.Method("calc_state")

    def calc_state(self, obj):
        if 'relay' in obj and obj.relay == 'open':
            return True

        return False
