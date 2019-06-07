from pygass import constants as st
from pygass.helper import make_request, global_params

__license__ = "GPL-3"

def track_pageview(client_id, page, hostname=None, title=None, **kwargs):
    """ Fire a page tracking EVENT

    Parameters
    ----------
    client_id : str
        Anonymous client id
    page : str
        The page url for example "/page/one"
    hostname : str, optional

    title : str, optional
        The page title human friendly version "Page one"
    ip : str, optional
        The clients ip address
    user_agent : str, optional
        The clients user_agent

    Returns
    -------
    response
        json response or image response if live url
    """
    st.track_pageview_dict[st.CLIENT_ID_ATTR] = client_id
    st.track_pageview_dict[st.PAGEVIEW_PAGE_ATTR] = page
    st.track_pageview_dict[st.PAGEVIEW_HOSTNAME_ATTR] = hostname
    st.track_pageview_dict[st.PAGEVIEW_TITLE_ATTR] = title
    return make_request(params=global_params(st.track_pageview_dict, **kwargs))


def track_event(client_id, category, action, label=None, value=None, **kwargs):
    """ Track an event on the site.

    Parameters
    ----------
    client_id : str
        Anonymous client id
    category : str
        The events category "video" for example
    action : str, optional
        The action applied "play" for example
    label : str, optional
        The events label "holiday" for example
    value : str, optional
        The events value "300" for example
    ip : str, optional
        The clients ip address
    user_agent : str, optional
        The clients user_agent


    Returns
    -------
    response
        json response or image response if live url
    """

    st.track_event_dict[st.CLIENT_ID_ATTR] = client_id
    st.track_event_dict[st.EVENT_CATEGORY_ATTR] = category
    st.track_event_dict[st.EVENT_ACTION_ATTR] = action
    st.track_event_dict[st.EVENT_LABEL_ATTR] = label
    st.track_event_dict[st.EVENT_VALUE_ATTR] = value
    return make_request(params=global_params(st.track_event_dict, **kwargs))


def track_transaction(
    client_id,
    transaction_id,
    affiliation=None,
    revenue=None,
    shipping=None,
    tax=None,
    currency_code=None,
    **kwargs,
):
    """ Track a site transaction on the site.

    Parameters
    ----------
    client_id : str
        Anonymous client id
    transaction_id : str
        The transactions unique id "tid01" for example
    affiliation : str, optional
        The affiliation "westernWear" for example
    revenue : str, optional
        The revenue "50.00" for example
    shipping : str, optional
        The shipping cost "32.00" for example
    tax : str, optional
        The tax amount "12.00" for example
    currency_code : str, optional
        The transactions currency "GBP" for example
    ip : str, optional
        The clients ip address
    user_agent : str, optional
        The clients user_agent


    Returns
    -------
    response
        json response or image response if live url
    """

    st.track_transaction_dict[st.CLIENT_ID_ATTR] = client_id

    st.track_transaction_dict[st.TRANSACTION_ID_ATTR] = transaction_id
    st.track_transaction_dict[st.TRANSACTION_AFFILIATION_ATTR] = affiliation
    st.track_transaction_dict[st.TRANSACTION_REVENUE_ATTR] = revenue
    st.track_transaction_dict[st.TRANSACTION_SHIPPING_ATTR] = shipping
    st.track_transaction_dict[st.TRANSACTION_TAX_ATTR] = tax
    st.track_transaction_dict[
        st.TRANSACTION_CURRENCY_CODE_ATTR
    ] = currency_code
    return make_request(
        params=global_params(st.track_transaction_dict, **kwargs)
    )


def track_item(
    client_id,
    transaction_id,
    name,
    price=None,
    quantity=1,
    code=None,
    variation=None,
    currency=None,
    **kwargs,
):
    """ Track an item that is part of a transaction.

    Parameters
    ----------
    client_id : str
        Anonymous client id
    transaction_id : str
        The transactions unique id, should match a previous transaction id
        "tid01" for example
    name : str, optional
        The name "sofa" for example
    price : str, optional
        The items price "300.00" for example
    quantity : str, optional
        The quantity being purchased "1" for example
    code : str, optional
        The code / sku code "u3eqds43" for example
    variation : str, optional
        The variation code / category "furniture" for example
    currency_code : str, optional
        The transactions currency "GBP" for example
    ip : str, optional
        The clients ip address
    user_agent : str, optional
        The clients user_agent


    Returns
    -------
    response
        json response or image response if live url
    """

    st.track_item_dict[st.CLIENT_ID_ATTR] = client_id
    st.track_item_dict[st.TRANSACTION_ID_ATTR] = transaction_id
    st.track_item_dict[st.ITEM_NAME_ATTR] = name
    st.track_item_dict[st.ITEM_PRICE_ATTR] = price
    st.track_item_dict[st.ITEM_QUANTITY_ATTR] = quantity
    st.track_item_dict[st.ITEM_CODE_ATTR] = code
    st.track_item_dict[st.ITEM_VARIATION_ATTR] = variation
    st.track_item_dict[st.ITEM_CURRENCY_ATTR] = currency
    return make_request(params=global_params(st.track_item_dict, **kwargs))


def track_social(client_id, action, network, target, **kwargs):
    """ Track an social event.

    Parameters
    ----------
    client_id : str
        Anonymous client id
    action : str
        The social action "like" for example
    network : str, optional
        The network used "facebook" for example
    target : str, optional
        The target of the interaction "/home" for example
    ip : str, optional
        The clients ip address
    user_agent : str, optional
        The clients user_agent


    Returns
    -------
    response
        json response or image response if live url
    """
    st.track_social_dict[st.CLIENT_ID_ATTR] = client_id
    st.track_social_dict[st.SOCIAL_ACTION_ATTR] = action
    st.track_social_dict[st.SOCIAL_NETWORK_ATTR] = network
    st.track_social_dict[st.SOCIAL_TARGET_ATTR] = target
    return make_request(params=global_params(st.track_social_dict, **kwargs))


