from ms_sdk.Entities.Entity import Entity


class CurrencyRate(Entity):

    id = None
    fromId = None
    toId = None
    rate = None
    lastUpdate = None