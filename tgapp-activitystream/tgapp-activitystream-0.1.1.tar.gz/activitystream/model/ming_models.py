from datetime import datetime

from activitystream import model
from ming import schema as s
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass
from pymongo import DESCENDING

from tg.i18n import ugettext as _
from tg.decorators import cached_property
from tgext.pluggable import instance_primary_key


def get_obj(type_, id_):
    model_ = model.provider.get_entity(type_)
    primary_field_ = model.provider.get_primary_field(model_)
    return model.provider.get_obj(
        model_,
        {primary_field_: id_}
    )


class Action(MappedClass):
    class __mongometa__:
        session = model.DBSession
        name = 'activity_stream_action'
        indexes = [
            (('actor_id', ), ('timestamp', DESCENDING)),
            ('actor_type', ),
            (('_recipients.recipient_id', ), ('timestamp', DESCENDING)),
            ('_recipients.recipient_type', ),
        ]

    _id = FieldProperty(s.ObjectId)

    actor_type = FieldProperty(s.String)
    actor_id = FieldProperty(s.ObjectId)

    verb = FieldProperty(s.String)

    description = FieldProperty(s.String)
    extra = FieldProperty(s.String)

    target_type = FieldProperty(s.String)
    target_id = FieldProperty(s.ObjectId)

    action_obj_type = FieldProperty(s.String)
    action_obj_id = FieldProperty(s.ObjectId)

    timestamp = FieldProperty(s.DateTime, if_missing=datetime.utcnow)

    _recipients = FieldProperty(s.Array(s.Object(fields={'_type': s.String, '_id': s.ObjectId})))

    @property
    def timestamp_24_hh_mm(self):
        return datetime.strftime(self.timestamp, '%X')

    @cached_property
    def actor(self, default=None):
        if not (self.actor_type and self.actor_id):
            return default
        entity = get_obj(self.actor_type, self.actor_id)
        return getattr(entity, 'as_str', entity)

    @cached_property
    def target(self, default=None):
        if not (self.target_type and self.target_id):
            return default
        entity = get_obj(self.target_type, self.target_id)
        return getattr(entity, 'as_str', entity)

    @property
    def target_link(self):
        entity = get_obj(self.target_type, self.target_id)
        return getattr(entity, 'as_link', None)

    @property
    def action_obj(self, default=None):
        if not (self.action_obj_type and self.action_obj_id):
            return default
        return get_obj(self.action_obj_type, self.action_obj_id)

    @property
    def timestamp_since(self):
        diff = datetime.utcnow() - self.timestamp

        minutes = diff.total_seconds() / 60

        if minutes <= 1:
            timestamp_since_ = _(u'less than 1 minute ago')
        elif int(minutes) == 1:
            timestamp_since_ = _(u'about 1 minute ago')
        elif minutes < 60:
            timestamp_since_ = _(u'about %s minutes ago') % int(minutes)
        elif 60 <= minutes < 119:
            timestamp_since_ = _(u'about 1 hour ago')
        elif minutes < 60 * 24:
            timestamp_since_ = _(u'about %s hours ago') % int(minutes/60)
        else:
            timestamp_since_ = datetime.strftime(self.timestamp, '%x')

        return timestamp_since_

    @property
    def recipients(self):
        return (get_obj(r._type, r._id) for r in self._recipients)

    @classmethod
    def get_by_recipient(cls, recipient):
        return cls.query.find({
            '$or': [{'_recipients._id': instance_primary_key(recipient)},
                    {'_recipients': {'$eq': None}}]
        }).sort('timestamp', DESCENDING)

    @classmethod
    def count_not_seen_by_recipient(cls, recipient):
        return cls.query.find({
            '$or': [
                {'_recipients._id': instance_primary_key(recipient)},
                {'_recipients': {'$eq': None}},
            ],
            'timestamp': {'$gt': recipient.last_activity_seen},
        }).count()

    @classmethod
    def render_str(cls, action, **kw):
        '''

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>
        '''

        timestamp_format = kw.get('timestamp_format', lambda t: datetime.strftime(t, '%x'))
        timestamp_since = None

        if kw.get('timestamp_since', False):
            timestamp_since = action.timestamp_since

        str_ = u'{actor} {verb} {action_object} {target} {time}'.format(
            actor=action.actor,
            verb=action.verb,
            target=action.target or '',
            action_object=action.action_obj or '',
            time=timestamp_since or timestamp_format(action.timestamp))

        return str_
