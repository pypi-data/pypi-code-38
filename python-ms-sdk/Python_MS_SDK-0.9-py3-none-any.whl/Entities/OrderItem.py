from ms_sdk.Entities.Entity import Entity


class OrderItem(Entity):

    id = None
    orderId = None
    amount = None
    promotionId = None
    compound = None
    itemPrice = None
    itemDiscountPrice = None
    itemPriceWithDiscount = None
    vatId = None
    itemVatPrice = None
    itemVatExcludePrice = None
    totalPrice = None

    product = None
