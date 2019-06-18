from ms_sdk.Entities.Entity import Entity


class User(Entity):

    id = None
    email = None
    password = None
    name = None
    surname = None
    active = None
    isSubscriber = 0
    guid = None
    avatar = None

    defaultAddressId = None
    langId = None
    basketId = None