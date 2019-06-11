from .instagram_query_id import InstagramQueryId

import urllib.parse
import json
from json import JSONEncoder


BASE_URL = 'https://www.instagram.com'
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
ACCOUNT_PAGE = 'https://www.instagram.com/{username}'
MEDIA_LINK = 'https://www.instagram.com/p/{code}'
ACCOUNT_MEDIAS = 'https://www.instagram.com/graphql/query/?query_hash=42323d64886122307be10013ad2dcc44&variables={variables}'
ACCOUNT_JSON_INFO = 'https://www.instagram.com/{username}/?__a=1'
MEDIA_JSON_INFO = 'https://www.instagram.com/p/{code}/?__a=1'
MEDIA_JSON_BY_LOCATION_ID = 'https://www.instagram.com/explore/locations/{{facebookLocationId}}/?__a=1&max_id={{maxId}}'
MEDIA_JSON_BY_TAG = 'https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={max_id}'
GENERAL_SEARCH = 'https://www.instagram.com/web/search/topsearch/?query={query}'
ACCOUNT_JSON_INFO_BY_ID = 'ig_user({userId}){id,username,external_url,full_name,profile_pic_url,biography,followed_by{count},follows{count},media{count},is_private,is_verified}'
COMMENTS_BEFORE_COMMENT_ID_BY_CODE = 'https://www.instagram.com/graphql/query/?query_hash=33ba35852cb50da46f5b5e889df7d159&variables={variables}'
LAST_LIKES_BY_CODE = 'ig_shortcode({{code}}){likes{nodes{id,user{id,profile_pic_url,username,follows{count},followed_by{count},biography,full_name,media{count},is_private,external_url,is_verified}},page_info}}'
LIKES_BY_SHORTCODE = 'https://www.instagram.com/graphql/query/?query_id=17864450716183058&variables={"shortcode":"{{shortcode}}","first":{{count}},"after":"{{likeId}}"}'
FOLLOWING_URL = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&id={{accountId}}&first={{count}}&after={{after}}'
FOLLOWERS_URL = 'https://www.instagram.com/graphql/query/?query_id=17851374694183129&id={{accountId}}&first={{count}}&after={{after}}'
FOLLOW_URL = 'https://www.instagram.com/web/friendships/{{accountId}}/follow/'
UNFOLLOW_URL = 'https://www.instagram.com/web/friendships/{{accountId}}/unfollow/'
USER_FEED = 'https://www.instagram.com/graphql/query/?query_id=17861995474116400&fetch_media_item_count=12&fetch_media_item_cursor=&fetch_comment_count=4&fetch_like=10'
USER_FEED2 = 'https://www.instagram.com/?__a=1'
INSTAGRAM_QUERY_URL = 'https://www.instagram.com/query/'
INSTAGRAM_CDN_URL = 'https://scontent.cdninstagram.com/'
ACCOUNT_JSON_PRIVATE_INFO_BY_ID = 'https://i.instagram.com/api/v1/users/{userId}/info/'
LIKE_URL = 'https://www.instagram.com/web/likes/{mediaId}/like/'
UNLIKE_URL = 'https://www.instagram.com/web/likes/{mediaId}/unlike/'
ADD_COMMENT_URL = 'https://www.instagram.com/web/comments/{mediaId}/add/'
DELETE_COMMENT_URL = 'https://www.instagram.com/web/comments/{mediaId}/delete/{commentId}/'

ACCOUNT_MEDIAS2 = 'https://www.instagram.com/graphql/query/?query_id=17880160963012870&id={{accountId}}&first=10&after='

    # Look alike??
URL_SIMILAR = 'https://www.instagram.com/graphql/query/?query_id=17845312237175864&id=4663052'

GRAPH_QL_QUERY_URL = 'https://www.instagram.com/graphql/query/?query_id={{queryId}}'

request_media_count = 30

def get_account_page_link(username):
    return ACCOUNT_PAGE.replace('{username}', urllib.parse.quote_plus(username))

def get_account_json_link(username):
    return ACCOUNT_JSON_INFO.replace('{username}', urllib.parse.quote_plus(username))

def get_account_json_info_link_by_account_id(account_id):
    return ACCOUNT_JSON_INFO_BY_ID.replace('{userId}', urllib.parse.quote_plus(account_id))

def get_account_json_private_info_link_by_account_id(account_id):
    return ACCOUNT_JSON_PRIVATE_INFO_BY_ID.replace('{userId}', urllib.parse.quote_plus(str(account_id)))

def get_account_medias_json_link(variables):
    return ACCOUNT_MEDIAS.replace('{variables}', urllib.parse.quote_plus(json.dumps(variables)))

def get_media_page_link(code):
    return MEDIA_LINK.replace('{code}', urllib.parse.quote_plus(code))

def get_media_json_link(code):
    return MEDIA_JSON_INFO.replace('{code}', urllib.parse.quote_plus(code))

def get_medias_json_by_location_id_link(facebookLocationId, maxId=''):
    url = MEDIA_JSON_BY_LOCATION_ID.replace(
        '{{facebookLocationId}}', urllib.parse.quote_plus(str(facebookLocationId)))
    return url.replace('{{maxId}}', urllib.parse.quote_plus(maxId))

def get_medias_json_by_tag_link(tag, maxId=''):
    url = MEDIA_JSON_BY_TAG.replace(
        '{tag}', urllib.parse.quote_plus(tag))
    return url.replace('{max_id}', urllib.parse.quote_plus(maxId))

def get_general_search_json_link(query):
    return GENERAL_SEARCH.replace('{query}', urllib.parse.quote_plus(query))

def get_comments_before_comments_id_by_code(variables):
    return COMMENTS_BEFORE_COMMENT_ID_BY_CODE.replace('{variables}', urllib.parse.quote_plus(variables))

def get_last_likes_by_code_link(code):
    return LAST_LIKES_BY_CODE.replace('{{code}}', urllib.parse.quote_plus(code))

def get_last_likes_by_code(code, count, lastLikeID):
    url = LIKES_BY_SHORTCODE.replace(
        '{{shortcode}}', urllib.parse.quote_plus(code))
    url = url.replace('{{count}}', urllib.parse.quote_plus(str(count)))
    url = url.replace('{{likeId}}', urllib.parse.quote_plus(str(lastLikeID)))

    return url

def get_follow_url(accountId):
    return FOLLOW_URL.replace('{{accountId}}', urllib.parse.quote_plus(accountId))

def get_unfollow_url(accountId):
    return UNFOLLOW_URL.replace('{{accountId}}', urllib.parse.quote_plus(accountId))

def get_followers_json_link(accountId, count, after=''):
    url = FOLLOWERS_URL.replace(
        '{{accountId}}', urllib.parse.quote_plus(accountId))
    url = url.replace('{{count}}', urllib.parse.quote_plus(str(count)))

    if (after == ''):
        url = url.replace('&after={{after}}', '')
    else:
        url = url.replace('{{after}}', urllib.parse.quote_plus(str(after)))

    return url

def get_following_json_link(accountId, count, after=''):
    url = FOLLOWING_URL.replace(
        '{{accountId}}', urllib.parse.quote_plus(accountId))
    url = url.replace('{{count}}', urllib.parse.quote_plus(count))

    if (after == ''):
        url = url.replace('&after={{after}}', '')
    else:
        url = url.replace('{{after}}', urllib.parse.quote_plus(after))

    return url

def get_user_stories_link():
    return get_graph_ql_url(InstagramQueryId.USER_STORIES, {'variables': JSONEncoder().encode([])})

def get_graph_ql_url(queryId, parameters):
    url = GRAPH_QL_QUERY_URL.replace(
        '{{queryId}}', urllib.parse.quote_plus(queryId))
    if (len(parameters) > 0):
        query_string = urllib.parse.urlencode(parameters)
        url += '&' + query_string

    return url

def get_stories_link(variables):
    return get_graph_ql_url(InstagramQueryId.STORIES, {'variables': JSONEncoder().encode(variables)})

def get_like_url(mediaId):
    return LIKE_URL.replace('{mediaId}', urllib.parse.quote_plus(mediaId))

def get_unlike_url(mediaId):
    return UNLIKE_URL.replace('{mediaId}', urllib.parse.quote_plus(mediaId))

def get_add_comment_url(mediaId):
    return ADD_COMMENT_URL.replace('{mediaId}', mediaId)


def get_delete_comment_url(mediaId, commentId):
    url = DELETE_COMMENT_URL.replace('{mediaId}', mediaId)
    url = url.replace('{commentId}', commentId)
    return url
