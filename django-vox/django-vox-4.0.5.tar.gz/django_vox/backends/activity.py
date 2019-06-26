import json
from typing import List
from urllib.parse import urlsplit

import aspy
import django.db.transaction
import django.utils.encoding
from django.template import Context
from django.utils.translation import ugettext_lazy as _

import django_vox.base

from . import base

__ALL__ = ("Backend",)

PUBLIC_ADDRESS = "https://www.w3.org/ns/activitystreams#Public"


def id_to_user(ids: List[str]):
    import django_vox.registry

    for identifier in ids:
        url = django.utils.encoding.iri_to_uri(identifier)
        # I'm pretty sure we're only path matching, but this might change
        path = urlsplit(url)[2]
        # there should be a '/' in the beginning of the path, but that's
        # not normally part of the regex
        if path.startswith("/"):
            path = path[1:]
        # put the message in the relevant inbox
        yield django_vox.registry.objects.get_local_object(path)


class Backend(base.Backend):

    ID = "activity"
    PROTOCOL = "activity"
    VERBOSE_NAME = _("Activity Stream")
    USE_SUBJECT = True
    EDITOR_TYPE = "html-light"
    ALLOW_MANUAL_SENDING = False

    # aspy.Create is the default, don't need to use it
    ACTIVITIES = (
        aspy.Accept,
        aspy.TentativeAccept,
        aspy.Add,
        aspy.Delete,
        aspy.Follow,
        aspy.Ignore,
        aspy.Join,
        aspy.Leave,
        aspy.Like,
        aspy.Offer,
        aspy.Invite,
        aspy.Reject,
        aspy.TentativeReject,
        aspy.Remove,
        aspy.Undo,
        aspy.Update,
        aspy.View,
        aspy.Listen,
        aspy.Read,
        aspy.Move,
        aspy.Travel,
        aspy.Announce,
        aspy.Block,
        aspy.Flag,
        aspy.Dislike,
        aspy.Question,
    )
    ACTIVITY_MAP = dict(
        (activity.__name__.lower(), activity) for activity in ACTIVITIES
    )

    @classmethod
    def _build_summary(cls, body: str, context):
        template = base.template_from_string(body)
        return template.render(context)

    @classmethod
    def _build_subject(cls, subject: str, context):
        if subject == "":
            obj = context.get("object")
            if obj is not None:
                if hasattr(obj, "name"):
                    if isinstance(obj.name, str):
                        return obj.name
            return ""

        template = base.template_from_string(subject)
        return template.render(context)

    @classmethod
    def _build(cls, subject: str, body: str, parameters: dict):
        context = Context(parameters, autoescape=cls.ESCAPE_HTML)
        return cls._build_subject(subject, context), cls._build_summary(body, context)

    @staticmethod
    def to_activity_object(obj):
        if isinstance(obj, (aspy.Object, aspy.Link)):
            return obj
        if hasattr(obj, "__activity__"):
            return obj.__activity__()
        if hasattr(obj, "get_absolute_url"):
            return django_vox.base.full_iri(obj.get_absolute_url())
        return None

    @classmethod
    def build_message(
        cls,
        subject: str,
        body: str,
        parameters: dict,
        _attachments: List[base.AttachmentData],
    ):
        subject, summary = cls._build(subject, body, parameters)
        activity_type = parameters.get("activity_type")
        if activity_type is None:
            normalized_codename = parameters["notification"].codename.lower()
            activity_type = cls.ACTIVITY_MAP.get(normalized_codename, aspy.Create)
        activity_actor = cls.to_activity_object(parameters.get("actor"))
        activity_target = cls.to_activity_object(parameters.get("target"))
        activity = activity_type(
            name=subject, summary=summary, object=parameters["activity_object"]
        )
        if activity_actor is not None:
            activity["actor"] = activity_actor
        if activity_target is not None:
            activity["target"] = activity_target
        return str(activity)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        subject, summary = cls._build(subject, body, parameters)
        return "<div><strong>{}</strong></div>" "<div>{}</div".format(subject, summary)

    def send_message(self, _from_address: str, to_addresses: List[str], message: str):
        import django_vox.models

        address_set = set(to_addresses)
        # note: we don't support public addressing yet, just strip them
        if PUBLIC_ADDRESS in address_set:
            address_set.remove(PUBLIC_ADDRESS)
        users = id_to_user(address_set)
        json_data = json.loads(message)
        kwargs = {}
        for field in ("actor", "object", "target"):
            field_data = json_data.get(field)
            if isinstance(field_data, str):
                kwargs[field + "_id"] = field_data
                kwargs[field + "_json"] = ""
            elif isinstance(field_data, dict):
                field_id = field_data.get("id")
                if field_id is not None:
                    kwargs[field + "_id"] = field_id
                kwargs[field + "_json"] = json.dumps(field_data)

        for field in ("name", "summary", "type"):
            if field in json_data:
                kwargs[field] = json_data[field]

        with django.db.transaction.atomic():
            activity = django_vox.models.Activity.objects.create(**kwargs)
            for user in users:
                django_vox.models.InboxItem.objects.create(
                    activity=activity, owner=user
                )
