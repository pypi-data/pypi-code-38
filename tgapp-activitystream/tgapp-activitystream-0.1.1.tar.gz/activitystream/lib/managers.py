from tgext.pluggable import primary_key, instance_primary_key

from activitystream import model


class ActionManager(object):

    def create(self, actor, verb, target=None, action_obj=None, description=None, extra=None,
               recipients=None):

        actor_id = primary_key(actor.__class__).name
        target_id = primary_key(target.__class__).name if target else ''
        action_obj_id = primary_key(action_obj.__class__).name if action_obj else ''

        _recipients = None
        if recipients:
            _recipients = [{'_type': r.__class__.__name__,
                            '_id': instance_primary_key(r)} for r in recipients]

        return model.provider.create(
            model.Action,
            dict(
                actor_type=actor.__class__.__name__,
                actor_id=getattr(actor, actor_id),
                verb=verb,
                target_type=target.__class__.__name__ if target else None,
                target_id=getattr(target, target_id, None),
                action_obj_type=action_obj.__class__.__name__ if action_obj else None,
                action_obj_id=getattr(action_obj, action_obj_id, None),
                description=description,
                extra=extra,
                _recipients=_recipients,
            )
        )

    def get_actions(self, limit=None, order_by='timestamp', desc=True, **kwargs):
        action = model.provider.query(
            model.Action,
            limit=limit,
            order_by=order_by,
            desc=desc,
            **kwargs)

        return action

    def get_by_recipient(cls, recipient):
        return model.Action.get_by_recipient(recipient)

    def count_not_seen_by_recipient(cls, recipient):
        return model.Action.count_not_seen_by_recipient(recipient)


am = ActionManager()
