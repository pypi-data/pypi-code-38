ANALYTICS_URL = "https://www.google-analytics.com/collect"
ANALYTICS_URL = "https://www.google-analytics.com/debug/collect"
ANALYTICS_CODE = "UA-XXXXX-Y"
ANALYTICS_VERSION = "1"
ANALYTICS_TIMEOUT = 1.5

VERSION_ATTR = "v"
TRACKING_ID_ATTR = "tid"
CLIENT_ID_ATTR = "cid"
TYPE_ATTR = "t"

PAGEVIEW_HOSTNAME_ATTR = "dh"
PAGEVIEW_PAGE_ATTR = "dp"
PAGEVIEW_TITLE_ATTR = "dt"
DOCUMENT_REFERRER = "dr"

EVENT_CATEGORY_ATTR = "ec"
EVENT_ACTION_ATTR = "ea"
EVENT_LABEL_ATTR = "el"
EVENT_VALUE_ATTR = "ev"

TRANSACTION_ID_ATTR = "ti"
TRANSACTION_AFFILIATION_ATTR = "ta"
TRANSACTION_REVENUE_ATTR = "tr"
TRANSACTION_SHIPPING_ATTR = "ts"
TRANSACTION_TAX_ATTR = "tt"
TRANSACTION_CURRENCY_CODE_ATTR = "cu"

ITEM_NAME_ATTR = "in"
ITEM_PRICE_ATTR = "ip"
ITEM_QUANTITY_ATTR = "iq"
ITEM_CODE_ATTR = "ic"
ITEM_VARIATION_ATTR = "iv"
ITEM_CURRENCY_ATTR = "cu"

SOCIAL_ACTION_ATTR = "sa"
SOCIAL_NETWORK_ATTR = "sn"
SOCIAL_TARGET_ATTR = "st"

PROXY_SERVER_IP = "uip"
PROXY_SERVER_USER_AGENT = "ua"

NON_INTERACTION_HIT = "ni"
QUEUE_TIME = "qt"

CAMPAIGN_ID = "ci"
CAMPAIGN_NAME = "cn"
CAMPAIGN_SOURCE = "cs"
CAMPAIGN_MEDIUM = "cm"
CAMPAIGN_KEYWORD = "ck"
CAMPAIGN_CONTENT = "cc"

ECOMMERCE_ID = "il1pi1id"
ECOMMERCE_NAME = "il1pi1nm"
ECOMMERCE_LIST = "il1nm"
ECOMMERCE_BRAND = "il1pi1br"
ECOMMERCE_CATEGORY = "il1pi1ca"
ECOMMERCE_VARIANT = "il1pi1va"
ECOMMERCE_POSITION = "il1pi1ps"
ECOMMERCE_CUSTOM = "il1pi1cd1"
# ECOMMERCE_PRICE = "price"
# ECOMMERCE_COUPON = "coupon"

ECOMMERCE_PROMOTION_CREATIVE = "creative"

ECOMMERCE_ACTION_PRODUCT_ACTION = "pa"
ECOMMERCE_ACTION_PRODUCT_ID = "pr1id"
ECOMMERCE_ACTION_PRODUCT_QUANTITY = "pr1qt"

ECOMMERCE_ACTION_PRODUCT_NAME = "pr1nm"
ECOMMERCE_ACTION_PRODUCT_CATEGORY = "pr1ca"
ECOMMERCE_ACTION_PRODUCT_BRAND = "pr1br"
ECOMMERCE_ACTION_PRODUCT_VARIANT = "pr1va"
ECOMMERCE_ACTION_PRODUCT_POSITION = "pr1ps"
ECOMMERCE_ACTION_PRODUCT_LIST = "pal"

ECOMMERCE_PRODUCT_PURCHASE_PRODUCT_ID = "click"
ECOMMERCE_PRODUCT_PROMOTION_DETAIL = "detail"
ECOMMERCE_PRODUCT_PROMOTION_ADD = "add"
ECOMMERCE_PRODUCT_PROMOTION_REMOVE = "remove"
ECOMMERCE_PRODUCT_PROMOTION_CHECKOUT = "checkout"
ECOMMERCE_PRODUCT_PROMOTION_CHECKOUT_OPTION = "checkout_option"
ECOMMERCE_PRODUCT_PROMOTION_PURCHASE = "purchase"
ECOMMERCE_PRODUCT_PROMOTION_REFUND = "refund"
ECOMMERCE_PRODUCT_PROMOTION_PROMO_CLICK = "promo_click"

track_global = {
    PROXY_SERVER_IP: None,
    PROXY_SERVER_USER_AGENT: None,
    NON_INTERACTION_HIT: None,
    QUEUE_TIME: None,
    DOCUMENT_REFERRER: None,
    CAMPAIGN_ID: None,
    CAMPAIGN_NAME: None,
    CAMPAIGN_SOURCE: None,
    CAMPAIGN_MEDIUM: None,
    CAMPAIGN_KEYWORD: None,
    CAMPAIGN_CONTENT: None,
}

track_pageview_dict = dict(
    {
        VERSION_ATTR: ANALYTICS_VERSION,
        TRACKING_ID_ATTR: ANALYTICS_CODE,
        CLIENT_ID_ATTR: None,
        TYPE_ATTR: "pageview",
        PAGEVIEW_PAGE_ATTR: None,
        PAGEVIEW_HOSTNAME_ATTR: None,
        PAGEVIEW_TITLE_ATTR: None,
    },
    **track_global
)

track_social_dict = dict(
    {
        VERSION_ATTR: ANALYTICS_VERSION,
        TRACKING_ID_ATTR: ANALYTICS_CODE,
        CLIENT_ID_ATTR: None,
        TYPE_ATTR: "social",
        SOCIAL_ACTION_ATTR: None,
        SOCIAL_NETWORK_ATTR: None,
        SOCIAL_TARGET_ATTR: None,
    },
    **track_global
)


track_event_dict = dict(
    {
        VERSION_ATTR: ANALYTICS_VERSION,
        TRACKING_ID_ATTR: ANALYTICS_CODE,
        CLIENT_ID_ATTR: None,
        TYPE_ATTR: "event",
        EVENT_CATEGORY_ATTR: None,
        EVENT_ACTION_ATTR: None,
        EVENT_LABEL_ATTR: None,
        EVENT_VALUE_ATTR: None,
    },
    **track_global
)


track_transaction_dict = dict(
    {
        VERSION_ATTR: ANALYTICS_VERSION,
        TRACKING_ID_ATTR: ANALYTICS_CODE,
        CLIENT_ID_ATTR: None,
        TYPE_ATTR: "transaction",
        TRANSACTION_ID_ATTR: None,
        TRANSACTION_AFFILIATION_ATTR: None,
        TRANSACTION_REVENUE_ATTR: None,
        TRANSACTION_SHIPPING_ATTR: None,
        TRANSACTION_TAX_ATTR: None,
        TRANSACTION_CURRENCY_CODE_ATTR: None,
    },
    **track_global
)


track_item_dict = dict(
    {
        VERSION_ATTR: ANALYTICS_VERSION,
        TRACKING_ID_ATTR: ANALYTICS_CODE,
        CLIENT_ID_ATTR: None,
        TYPE_ATTR: "item",
        TRANSACTION_ID_ATTR: None,
        ITEM_NAME_ATTR: None,
        ITEM_PRICE_ATTR: None,
        ITEM_QUANTITY_ATTR: None,
        ITEM_CODE_ATTR: None,
        ITEM_VARIATION_ATTR: None,
        ITEM_CURRENCY_ATTR: None,
    },
    **track_global
)

enhanced_ecommerce_immpression = dict(
    {
        ECOMMERCE_ID: None,
        ECOMMERCE_NAME: None,
        ECOMMERCE_LIST: None,
        ECOMMERCE_BRAND: None,
        ECOMMERCE_CATEGORY: None,
        ECOMMERCE_VARIANT: None,
        ECOMMERCE_POSITION: None,
    },
    **track_pageview_dict
)


enhanced_ecommerce_action = dict(
    {
        **track_pageview_dict,
        **{
            ECOMMERCE_ACTION_PRODUCT_ACTION: None,
            ECOMMERCE_ACTION_PRODUCT_LIST: None,
            ECOMMERCE_ACTION_PRODUCT_ID: None,
            ECOMMERCE_ACTION_PRODUCT_NAME: None,
            ECOMMERCE_ACTION_PRODUCT_CATEGORY: None,
            ECOMMERCE_ACTION_PRODUCT_BRAND: None,
            ECOMMERCE_ACTION_PRODUCT_VARIANT: None,
            ECOMMERCE_ACTION_PRODUCT_POSITION: None,
            ECOMMERCE_ACTION_PRODUCT_QUANTITY: 1,
        },
    }
)


enhanced_ecommerce_action_impression = dict(
    {**enhanced_ecommerce_immpression, **enhanced_ecommerce_action}
)


enhanced_ecommerce_purchase = dict(
    {
        **enhanced_ecommerce_action,
        **{
            TRANSACTION_ID_ATTR: None,
            TRANSACTION_AFFILIATION_ATTR: None,
            TRANSACTION_REVENUE_ATTR: None,
            TRANSACTION_SHIPPING_ATTR: None,
            TRANSACTION_TAX_ATTR: None,
        },
    }
)
