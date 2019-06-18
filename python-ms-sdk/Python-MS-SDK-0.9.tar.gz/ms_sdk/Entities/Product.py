from ms_sdk.Entities.Entity import Entity
from ms_sdk.Lib.Mixins.InteractsWithAttributes import InteractsWithAttributesMixin


class Product(Entity, InteractsWithAttributesMixin):

    id = None
    urlCode = None
    title = None
    shortDescription = None
    fullDescription = None
    seoTitle = None
    seoDescription = None
    seoKeywords = None
    visible = None
    purchasePrice = None
    price = None
    oldPrice = None
    importedId = None
    variantsCompound = None

    attributes = []
    brand = None
    functionalName = None

    media = []
    mainMedia = None
