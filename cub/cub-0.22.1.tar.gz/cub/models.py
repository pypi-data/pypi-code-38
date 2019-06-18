from .compat import string_types
from .transport import API, json, json_datetime_hook


def objects_from_json(json_content, api_key=None):
    if isinstance(json_content, string_types):
        try:
            content = json.loads(json_content, object_hook=json_datetime_hook)
        except ValueError:
            return json_content
        return objects_from_json(content, api_key)
    elif isinstance(json_content, list):
        return [objects_from_json(obj, api_key) for obj in json_content]
    elif isinstance(json_content, dict):
        obj = json_content.get('object', None)
        if obj:
            id = json_content['id']
            klass = {
                'user': User,
                'organization': Organization,
                'member': Member,
                'position': Position,
                'memberposition': MemberPosition,
                'group': Group,
                'groupmember': GroupMember,
                'servicesubscription': ServiceSubscription,
                'plan': Plan,
                'customer': Customer,
                'site': Site,
                'mailinglist': MailingList,
                'subscription': Subscription,
                'country': Country,
                'state': State,
                'product': Product,
                'sku': SKU,
                'order': Order,
                'orderitem': OrderItem,
                'charge': Charge,
                'lead': Lead,
                'message': Message,
                'usersite': UserSite,
            }.get(obj, CubObject)
            return klass(api_key=api_key, id=id).load_from(json_content)
        else:
            return json_content


class CubObject(object):

    def __init__(self, api_key=None, id=None, deleted=False, **kwargs):
        self.id = id
        self.api_key = api_key
        self.deleted = deleted
        self._values = {'deleted': deleted}
        self.load_from(kwargs)

    def __setattr__(self, key, value):
        if hasattr(self, '_values'):
            self._values[key] = value
        return super(CubObject, self).__setattr__(key, value)

    def __repr__(self):
        return '%s id=%s: %s' % (self.__class__.__name__, self.id, self._values)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __eq__(self, other):
        if not hasattr(other, '_values'):
            return False
        if len(self._values) != len(other._values):
            return False
        for k, v in self._values.items():
            if not hasattr(other, k) or self._values[k] != other._values[k]:
                return False
        return True

    @classmethod
    def class_url(cls):
        return '/%ss' % cls.__name__.lower()

    def instance_url(self):
        assert self.id is not None, 'Unable to determine instance URL, '\
                                    'because %s.id is None.' \
                                    '' % self.__class__.__name__
        return '%s/%s' % (self.class_url(), self.id)

    def load_from(self, dikt):
        if dikt is None:
            return self
        for k, v in dikt.items():
            if isinstance(v, (dict, list)):
                v = objects_from_json(v, self.api_key)
            self.__setattr__(k, v)
        return self

    def reload(self, **kwargs):
        response = API(self.api_key).request('get', self.instance_url(), kwargs)
        return self.load_from(response)

    @classmethod
    def get(cls, id, api_key=None, **kwargs):
        instance = cls(api_key=api_key, id=id)
        return instance.reload(**kwargs)


class CreatableObject(CubObject):
    @classmethod
    def create(cls, api_key=None, **kwargs):
        api = API(api_key)
        response = api.request('post', cls.class_url(), params=kwargs)
        return objects_from_json(response, api.api_key)


class UpdatableObject(CubObject):
    def save(self):
        if self.id:
            response = API(self.api_key).request(
                'post',
                self.instance_url(),
                params=self._values
            )
        else:
            response = API(self.api_key).request(
                'post',
                self.__class__.class_url(),
                params=self._values
            )
        return self.load_from(response)


class ListableObject(CubObject):
    @classmethod
    def list(cls, api_key=None, **kwargs):
        response = API(api_key).request('get', cls.class_url(), kwargs)
        return objects_from_json(response, api_key=api_key)


class RemovableObject(CubObject):
    def delete(self):
        response = API(self.api_key).request('delete', self.instance_url())
        return self.load_from(response)

    @classmethod
    def delete_id(cls, id, api_key=None):
        instance = cls(api_key=api_key, id=id)
        return instance.delete()


# -------------- User objects -------------- #


class User(UpdatableObject):
    def load_from(self, dikt):
        if 'token' in dikt:
            self.api_key = dikt['token']
        return super(User, self).load_from(dikt)

    @classmethod
    def class_url(cls):
        return '/user'

    def instance_url(self):
        return '/users/%s' % self.id if self.id else self.class_url()

    @classmethod
    def get(cls, api_key=None, **kwargs):
        instance = cls(api_key=api_key)
        return instance.reload(**kwargs)

    @classmethod
    def login(cls, username, password, provider=None, api_key=None):
        provider = provider or ''
        url = '%s/%s' % (cls.class_url(), 'login')
        response = API(api_key).request('post', url, {
            'username': username,
            'password': password,
            'provider': provider,
        })
        return cls().load_from(response)

    def reissue_token(self, **kwargs):
        url = '%s/%s' % (self.class_url(), 'reissue-token')
        response = API(self.api_key).request('post', url, kwargs)
        return self.load_from(response)


class Organization(ListableObject):
    pass


class Position(ListableObject):
    pass


class Member(CreatableObject, UpdatableObject, RemovableObject, ListableObject):
    pass


class MemberPosition(CreatableObject, UpdatableObject,
                     RemovableObject, ListableObject):
    pass


class Group(CreatableObject, UpdatableObject, RemovableObject, ListableObject):
    pass


class GroupMember(CreatableObject, RemovableObject, ListableObject):
    pass


class Plan(CubObject):
    pass


class Customer(CreatableObject, ListableObject):
    pass


class ServiceSubscription(ListableObject):
    pass


class Site(ListableObject):
    pass


class MailingList(ListableObject):
    pass


class Subscription(ListableObject):
    pass


class Country(ListableObject):
    @classmethod
    def class_url(cls):
        return '/countries'


class State(ListableObject):
    pass


class Product(CubObject):
    pass


class SKU(CubObject):
    pass


class Order(CreatableObject, UpdatableObject, RemovableObject, ListableObject):
    pass


class OrderItem(CreatableObject, UpdatableObject, RemovableObject,
                ListableObject):
    pass


class Charge(ListableObject):
    pass


class Lead(ListableObject):
    pass


class Message(ListableObject):
    pass


class UserSite(ListableObject):
    pass
