import datetime
from marshmallow import Schema, fields

class GrowSchema(Schema):
    class META:
        strict = True

    id = fields.Integer(dump_only=True)
    name = fields.Str(
                required=True,
                error_messages={'required': 'name is required'})
    room_id = fields.Integer(
                required=True,
                error_messages={'required': 'room_id is required'})
    started = fields.DateTime(dump_only=True)
    transition = fields.DateTime()
    ended = fields.DateTime()
    status = fields.Method("calculate_grow", dump_only=True)

    def calculate_grow(self, obj):
        data = {
            'progress': [],
            'final': []
        }
        today = datetime.date.today()

        if not obj.ended:
            if obj.transition:
                data['progress'] = [(today - obj.transition.date()).days, 'flower']
            else:
                data['progress'] = [(today - obj.started.date()).days, 'growth']

            return "day {} of {}".format(*data['progress'])
        else:
            data['final'] += [(obj.ended - obj.started.date()).days, 'total']
            if obj.transition:
                data['final'] += [(obj.transition - obj.started.date()).days, 'growth']
                data['final'] += [(obj.ended - obj.transition.date()).days, 'flower']
            else:
                data['final'] += [(obj.end - obj.started.date()).days, 'growth']
                data['final'] += [0, 'flower']

            return "{} days {}, {} days {}, {} days {}".format(*data['final'])
