from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.contenttypes.models import ContentType


def log_action(user, model_object, message, create=True):
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(model_object).pk,
        object_id=model_object.id,
        object_repr=str(model_object),
        action_flag=ADDITION if create else CHANGE,
        change_message=message,
    )
