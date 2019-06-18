from ms_sdk.Entities.Entity import Entity


class ProductPriceConfiguration(Entity):

    id = None
    productId = None
    affectedAttributes = None
    priceTable = {}