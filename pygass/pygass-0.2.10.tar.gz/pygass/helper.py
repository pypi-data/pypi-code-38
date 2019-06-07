import requests

from pygass import constants as st


def make_request(params):
    """ Simple wrapper around requests.post

    Parameters
    ----------
    params : dict
        Python dictonary of values to send to google

    Returns
    -------
    response
        json response or image response if live url
    """
    params[st.TRACKING_ID_ATTR] = st.ANALYTICS_CODE
    response = requests.post(
        st.ANALYTICS_URL, params=params, timeout=st.ANALYTICS_TIMEOUT
    )
    response.raise_for_status()
    if (
        response.headers["content-type"]
        == "application/javascript; charset=utf-8"
    ):
        return response.json()

    return response.content


def global_params(track_dict, **kwargs):
    """ Simple wrapper to add ip and user_agent to the analytics requests
    see this link for details https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide#using-a-proxy-server


    Parameters
    ----------
    params : dict
        Python dictonary of values to send to google
    ip : str, optional
        Users ip address
    user_agent: str, optional
        Users browser / agent used to make the request
    Returns
    -------
    response
        dict
            Returned dict with appended ip and user_agent

"""
    track_dict[st.PROXY_SERVER_IP] = kwargs.get("ip")
    track_dict[st.PROXY_SERVER_USER_AGENT] = kwargs.get("user_agent")
    track_dict[st.NON_INTERACTION_HIT] = kwargs.get("non_interaction_hit")
    track_dict[st.QUEUE_TIME] = kwargs.get("queue_time")
    track_dict[st.DOCUMENT_REFERRER] = kwargs.get("document_referrer")

    track_dict[st.CAMPAIGN_ID] = kwargs.get("campaign_id")
    track_dict[st.CAMPAIGN_NAME] = kwargs.get("campaign_name")
    track_dict[st.CAMPAIGN_SOURCE] = kwargs.get("campaign_source")
    track_dict[st.CAMPAIGN_MEDIUM] = kwargs.get("campaign_medium")
    track_dict[st.CAMPAIGN_KEYWORD] = kwargs.get("campaign_keyword")
    track_dict[st.CAMPAIGN_CONTENT] = kwargs.get("campaign_content")
    return track_dict
