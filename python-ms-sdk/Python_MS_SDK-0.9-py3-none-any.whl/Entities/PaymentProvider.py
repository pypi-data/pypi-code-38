from ms_sdk.Entities.Entity import Entity


class PaymentProvider(Entity):

    id = None
    title = None
    className = None
    msUrl = None
    merchantId = None
    postUrl = None
    secretKey = None
    keyVersion = None
    apiKey = None
    shaIn = None
    shaOut = None
    autoReturnUrl = None
    returnUrl = None