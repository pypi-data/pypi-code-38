import datetime
import json
import re

import isodate


# utility functions


def camelize(string, uppercase_first_letter=True):
    # copied from the inflection module
    if uppercase_first_letter:
        return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)
    else:
        return string[0].lower() + camelize(string)[1:]


# base vocabulary


def as_uri(text):
    return "https://www.w3.org/ns/activitystreams#" + text


def as_prop(text):
    return camelize(text, False)


class _Base:
    TYPE_PROPERTIES = []
    CONTEXT = "https://www.w3.org/ns/activitystreams"

    def __init__(self, **kwargs):
        self.__immutable = False
        self.extra_context = {}
        self._props = {"type": self.get_type()}
        if "id" in kwargs:
            value = kwargs.pop("id")
            if value:
                self._props["id"] = value

        for k, v in kwargs.items():
            if k in self.TYPE_PROPERTIES:
                self._props[k] = v
            elif k.startswith("http://") or k.startswith("https://"):
                # lets find a nice slug
                slug = re.match(r".*?(\w+)$", k).group(1)
                if slug not in self.extra_context:
                    self.extra_context[slug] = k
                self._props[slug] = v
            else:
                raise TypeError("Unrecognized property {}".format(k))

    @classmethod
    def get_type(cls):
        return as_uri(cls.__name__)

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def __getitem__(self, item):
        return self._props[item]

    def __setitem__(self, key, value):
        if self.__immutable:
            raise TypeError("Object is immutable, unable to set {}".format(key))

        if key in self.TYPE_PROPERTIES:
            self._props[key] = value
        elif key.startswith("http://") or key.startswith("https://"):
            # lets find a nice slug
            slug = re.match(r".*?(\w+)$", key).group(1)
            if slug not in self.extra_context:
                self.extra_context[slug] = key
            self._props[slug] = value
        else:
            raise TypeError("Unrecognized property {}".format(key))

    def __contains__(self, item):
        return item in self._props

    def set_immutable(self):
        self.__immutable = True

    def to_dict(self):
        obj = self.part_to_dict()
        if self.extra_context:
            obj["@context"] = [self.CONTEXT, self.extra_context]
        else:
            obj["@context"] = self.CONTEXT
        return obj

    def _coerce_prop(self, key, val):
        if hasattr(val, "part_to_dict"):
            val = val.part_to_dict()
        return PROPERTIES[key](val, self.CONTEXT)

    def _props_to_dict(self):
        for key, value in self._props.items():
            if key in PROPERTIES:
                value = self._coerce_prop(key, value)
            elif key in self.extra_context:
                full_key = self.extra_context[key]
                if full_key in EXTENSION_PROPERTIES:
                    value = EXTENSION_PROPERTIES[full_key](value, self.CONTEXT)
            else:
                raise TypeError("Unrecognized key {}".format(key))
            # if isinstance(value, (list, tuple)):
            #     values = value
            # value = [self._coerce_prop(key, val) for val in value]
            # if len(values) == 1:
            #     values = values[0]
            if key.startswith("@"):
                key = key[1:]
            elif key.startswith(self.CONTEXT):
                start = len(self.CONTEXT + 1)
                key = key[start:]
            yield as_prop(key), value

    def part_to_dict(self):
        if self._props["type"] == as_uri("Object"):
            if len(self._props) == 1:
                return None
            if len(self._props) == 2 and "id" in self._props:
                return {"id": self._props["id"]}
        return dict(self._props_to_dict())


class Object(_Base):
    TYPE_PROPERTIES = (
        "id",
        "attachment",
        "attributed_to",
        "audience",
        "content",
        "context",
        "name",
        "endTime",
        "generator",
        "icon",
        "image",
        "in_reply_to",
        "location",
        "preview",
        "published",
        "replies",
        "start_time",
        "summary",
        "tag",
        "updated",
        "url",
        "to",
        "bto",
        "cc",
        "bcc",
        "media_type",
        "duration",  # ActivityPub extensions
        "endpoints",
        "following",
        "followers",
        "inbox",
        "liked",
        "shares",
        "likes",
        "oauth_authorization_endpoint",
        "oauth_token_endpoint",
        "outbox",
        "preferred_username",
        "provide_client_key",
        "proxy_url",
        "shared_inbox",
        "sign_client_key",
        "source",
        "streams",
        "upload_media",
    )


class Link(_Base):
    TYPE_PROPERTIES = (
        "id",
        "href",
        "rel",
        "media_type",
        "name",
        "hreflang",
        "height",
        "width",
        "preview",
    )


class Activity(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + (
        "actor",
        "object",
        "target",
        "result",
        "origin",
        "instrument",
    )


class IntransitiveActivity(Activity):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + (
        "actor",
        "target",
        "result",
        "origin",
        "instrument",
    )


class Collection(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + (
        "total_items",
        "current",
        "first",
        "last",
        "items",
    )

    def part_to_dict(self):
        dict_part = super().part_to_dict()
        if "totalItems" not in dict_part and "items" in dict_part:
            dict_part["totalItems"] = len(dict_part["items"])
        return dict_part


class OrderedCollection(Collection):
    pass


class CollectionPage(Collection):
    PAGE_PROPERTIES = ("part_of", "next", "prev")
    TYPE_PROPERTIES = Collection.TYPE_PROPERTIES + PAGE_PROPERTIES


class OrderedCollectionPage(CollectionPage, OrderedCollection):
    TYPE_PROPERTIES = OrderedCollection.TYPE_PROPERTIES + CollectionPage.PAGE_PROPERTIES


class Accept(Activity):
    pass


class TentativeAccept(Accept):
    pass


class Add(Activity):
    pass


class Arrive(IntransitiveActivity):
    pass


class Create(Activity):
    pass


class Delete(Activity):
    pass


class Follow(Activity):
    pass


class Ignore(Activity):
    pass


class Join(Activity):
    pass


class Leave(Activity):
    pass


class Like(Activity):
    pass


class Offer(Activity):
    pass


class Invite(Offer):
    pass


class Reject(Activity):
    pass


class TentativeReject(Reject):
    pass


class Remove(Activity):
    pass


class Undo(Activity):
    pass


class Update(Activity):
    pass


class View(Activity):
    pass


class Listen(Activity):
    pass


class Read(Activity):
    pass


class Move(Activity):
    pass


class Travel(IntransitiveActivity):
    pass


class Announce(Activity):
    pass


class Block(Ignore):
    pass


class Flag(Activity):
    pass


class Dislike(Activity):
    pass


class Question(IntransitiveActivity):
    pass


# actors


class Application(Object):
    pass


class Group(Object):
    pass


class Organization(Object):
    pass


class Person(Object):
    pass


class Service(Object):
    pass


# Object/Link types


class Relationship(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + ("subject", "object", "relationship")


class Article(Object):
    pass


class Document(Object):
    pass


class Audio(Document):
    pass


class Image(Document):
    pass


class Video(Document):
    pass


class Note(Object):
    pass


class Page(Object):
    pass


class Event(Object):
    pass


class Place(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + (
        "accuracy",
        "altitude",
        "latitude",
        "longitude",
        "radius",
        "units",
    )


class Mention(Link):
    pass


class Profile(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + ("describes",)


class Tombstone(Object):
    TYPE_PROPERTIES = Object.TYPE_PROPERTIES + ("former_type", "deleted")


# properties


def noop(data, _context):
    return data


float_property = noop
string_property = noop
unit_property = noop
lang_property = noop
mime_property = noop
non_neg_int_property = noop
only_object = noop


def duration_property(data, _context):
    return isodate.duration_isoformat(data)


def datetime_property(data, _context):
    return isodate.datetime_isoformat(data)


def any_uri(uri, context):
    if uri.startswith(context):
        start = len(context)
        uri = uri[start:]
        if uri.startswith("#"):
            uri = uri[1:]
    return uri


def multi_prop(func):
    def inner(data, context):
        return [func(item, context) for item in data]

    return inner


def var_prop(func):
    def inner(data, context):
        if isinstance(data, list):
            if len(data) == 1:
                return func(data[0], context)
            return [func(item, context) for item in data]
        return func(data, context)

    return inner


def single_link_or_object(data, context):
    if isinstance(data, str):
        return any_uri(data, context)
    if isinstance(data, dict):
        if len(data.keys()) == 1 and "id" in data.keys():
            return any_uri(data["id"], context)
        return data
    if isinstance(data, _Base):
        return data.part_to_dict()
    raise TypeError("Invalid value for link | object {}".format(data))


link_or_object = var_prop(single_link_or_object)
link_or_uri = link_or_object
link_or_collection_page = link_or_object
link_or_collection = link_or_object
link_or_image = link_or_object
collection = only_object


def closed_property(data, context):
    if isinstance(data, bool):
        return data
    if isinstance(data, datetime.datetime):
        return datetime_property(data, context)
    return link_or_object(data, context)


PROPERTIES = {
    "id": any_uri,
    "type": any_uri,
    "actor": link_or_object,
    "attachment": link_or_object,
    "attributed_to": link_or_object,
    "audience": link_or_object,
    "bcc": link_or_object,
    "bto": link_or_object,
    "cc": link_or_object,
    "context": link_or_object,
    "current": link_or_collection_page,
    "first": link_or_collection_page,
    "next": link_or_collection_page,
    "prev": link_or_collection_page,
    "generator": link_or_object,
    "icon": link_or_image,
    "image": link_or_image,
    "in_reply_to": link_or_object,
    "instrument": link_or_object,
    "last": link_or_collection_page,
    "location": link_or_object,
    "items": multi_prop(single_link_or_object),
    "one_of": link_or_object,
    "any_of": link_or_object,
    "closed": closed_property,
    "origin": link_or_object,
    "object": link_or_object,
    "result": link_or_object,
    "replies": collection,
    "tag": link_or_object,
    "target": link_or_object,
    "to": link_or_object,
    "url": link_or_uri,
    "accuracy": float_property,
    "altitude": float_property,
    "content": string_property,
    "name": string_property,
    "duration": duration_property,
    "href": any_uri,
    "hreflang": lang_property,
    "part_of": link_or_collection,
    "latitude": float_property,
    "longitude": float_property,
    "media_type": mime_property,
    "start_time": datetime_property,
    "end_time": datetime_property,
    "published": datetime_property,
    "updated": datetime_property,
    "deleted": datetime_property,
    "radius": float_property,
    # missing rel
    "start_index": non_neg_int_property,
    "summary": string_property,
    "total_items": non_neg_int_property,
    "units": unit_property,
    "height": non_neg_int_property,
    "width": non_neg_int_property,
    "subject": link_or_object,
    "relationship": only_object,
    "describes": only_object,
    "former_type": only_object,
    # ActivityPub extensions
    "endpoints": any_uri,
    "following": any_uri,
    "followers": any_uri,
    "inbox": any_uri,
    "liked": any_uri,
    "shares": any_uri,
    "likes": any_uri,
    "oauth_authorization_endpoint": any_uri,
    "oauth_token_endpoint": any_uri,
    "outbox": any_uri,
    "preferred_username": string_property,
    "provide_client_key": any_uri,
    "proxy_url": any_uri,
    "shared_inbox": any_uri,
    "sign_client_key": any_uri,
    "source": link_or_uri,
    "streams": only_object,
    "upload_media": any_uri,
}

EXTENSION_PROPERTIES = {"https://schema.org/dateRead": datetime_property}
