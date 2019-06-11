from bs4 import BeautifulSoup
import requests
import re
import json
import hashlib
import os
from slugify import slugify

from .session_manager import CookieSessionManager

from .exception.instagram_auth_exception import InstagramAuthException
from .exception.instagram_exception import InstagramException
from .exception.instagram_not_found_exception import InstagramNotFoundException

from .model.account import Account
from .model.comment import Comment
from .model.like import Like
from .model.location import Location
from .model.media import Media
from .model.story import Story
from .model.user_stories import UserStories
from .model.tag import Tag

from .endpoints import endpoints

from .two_step_verification.console_verification import ConsoleVerification

class Instagram:
    HTTP_NOT_FOUND = 404
    HTTP_OK = 200
    HTTP_FORBIDDEN = 403
    HTTP_BAD_REQUEST = 400

    MAX_COMMENTS_PER_REQUEST = 300
    MAX_LIKES_PER_REQUEST = 50
    # 30 mins time limit on operations that require multiple self.__req
    PAGING_TIME_LIMIT_SEC = 1800
    PAGING_DELAY_MINIMUM_MICROSEC = 1000000  # 1 sec min delay to simulate browser
    PAGING_DELAY_MAXIMUM_MICROSEC = 3000000  # 3 sec max delay to simulate browser

    instance_cache = None

    def __init__(self):
        self.__req = requests.session()
        self.paging_time_limit_sec = Instagram.PAGING_TIME_LIMIT_SEC
        self.paging_delay_minimum_microsec = Instagram.PAGING_DELAY_MINIMUM_MICROSEC
        self.paging_delay_maximum_microsec = Instagram.PAGING_DELAY_MAXIMUM_MICROSEC

        self.session_username = None
        self.session_password = None
        self.user_session = None
        self.rhx_gis = None
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'


    @staticmethod
    def with_credentials(username, password, session_folder = None):
        '''
        param string username
        param string password
        param null sessionFolder
    
        return Instagram
        '''

        Instagram.instance_cache = None
        
        if session_folder == None:
            cwd = os.getcwd()
            session_folder = cwd + os.path.sep + 'sessions' + os.path.sep
        
        if isinstance(session_folder, str):
            
            Instagram.instance_cache = CookieSessionManager(session_folder, slugify(username) + '.txt')

        else:
            Instagram.instance_cache = session_folder
        
        Instagram.instance_cache.empty_saved_cookies()

        instance = Instagram()
        instance.session_username = username
        instance.session_password = password
    
        return instance

    def set_proxies(self, proxy):
        if proxy and isinstance(proxy, dict):
            self.__req.proxies = proxy

    def disable_proxies(self):
        self.__req.proxies = {}
        
    @staticmethod
    def set_account_medias_request_count(count):
        '''
        Set how many media objects should be retrieved in a single request
        param int count
        '''
        endpoints.request_media_count = count

    def get_account_by_id(self, id):
        '''
        param string $id

        return Account
        throws InstagramException
        throws InvalidArgumentException
        throws InstagramNotFoundException
        '''
        username = self.get_username_by_id(id)
        return self.get_account(username)

    def get_username_by_id(self, id):
        '''
        param string $id
        return string
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = self.__req.get(endpoints.get_account_json_private_info_link_by_account_id(
            id), headers=self.generate_headers(self.user_session))

        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException(
                'Failed to fetch account with given id')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()
        if json_response == None:
            raise InstagramException('Response does not JSON')

        if json_response['status'] != 'ok':
            message = json_response['message'] if (
                'message' in json_response.keys()) else 'Unknown Error'
            raise InstagramException(message)

        return json_response['user']['username']

    def generate_headers(self, session, gis_token=None):
        '''
        @param $session
        @param $gisToken
        @return array
        '''
        headers = {}
        if (session != None):
            cookies = ''

            for key in session.keys():
                cookies += f"{key}={session[key]}; "

            csrf = session['x-csrftoken'] if session['csrftoken'] == None else session['csrftoken']

            headers = {
                'cookie': cookies,
                'referer': endpoints.BASE_URL + '/',
                'x-csrftoken': csrf
            }

        if self.user_agent != None:
            headers['user-agent'] = self.user_agent

            if (gis_token != None):
                headers['x-instagram-gis'] = gis_token

        return headers
    

    def __generate_gis_token(self, variables):
        '''
        param $variables
        return string
        throws InstagramException
        '''
        rhx_gis = self.__get_rhx_gis() if self.__get_rhx_gis() != None else 'NULL'
        string_to_hash = ':'.join([rhx_gis, json.dumps(variables)])
        return hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

    def __get_rhx_gis(self):
        if self.rhx_gis == None:
            try:
                shared_data = self.__get_shared_data_from_page()
            except:
                raise InstagramException('Could not extract gis from page')

            if 'rhx_gis' in shared_data.keys():
                self.rhx_gis = shared_data['rhx_gis']
            else:
                self.rhx_gis = None
                

        return self.rhx_gis
        
    def __get_mid(self):
        'manually fetches the machine id from graphQL'
        response =self.__req.get('https://www.instagram.com/web/__mid/')

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)

        return response.text
        
    def __get_shared_data_from_page(self, url = endpoints.BASE_URL):
        '''
        param string $url
        return mixed|null
        throws InstagramException
        throws InstagramNotFoundException
         '''
        url.strip
        url = url.rstrip('/') + '/'
        response = self.__req.get(url, headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException(f"Page {url} not found")

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        return Instagram.extract_shared_data_from_body(response.text)


    @staticmethod
    def extract_shared_data_from_body(body):
        array = re.findall(r'_sharedData = .*?;</script>', body)
        if len(array) > 0:
            raw_json = array[0][len("_sharedData ="):-len(";</script>")]

            return json.loads(raw_json)

        return None


    @staticmethod
    def search_tags_by_tag_name(self, tag):
        '''
        param string tag
     
        return array
        throws InstagramException
        throws InstagramNotFoundException
        '''
        # TODO: Add tests and auth
        response = self.__req.get(endpoints.get_general_search_json_link(tag))

        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        try:
            status = json_response['status']
            if status != 'ok':
                raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')
        except KeyError:
            raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')

        try:
            hashtags_raw = json_response['hashtags']
            if len(hashtags_raw) == 0:
                return []
        except KeyError:
            return []

        hashtags = []
        for json_hashtag in hashtags_raw:
            hashtags.append(Tag(json_hashtag['hashtag']))

        return hashtags

    def get_medias(self, username, count=20, maxId=''):
        '''
        param string username
        param int count
        param string maxId

        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''

        account = self.get_account(username)
        return self.get_medias_by_user_id(account.identifier, count, maxId)

        
    def get_medias_by_code(self, media_code):
        '''
        param string mediaCode (for example BHaRdodBouH)
   
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        url = endpoints.get_media_page_link(media_code)
        return self.get_media_by_url(url)

    def get_medias_by_user_id(self, id, count = 12, max_id = ''):
        '''
        param int id
        param int count
        param string maxId
     
        return Media[]
        throws InstagramException
        '''
        
        index = 0
        medias = []
        is_more_available = True

        while index < count and is_more_available:

            variables = {
                'id': str(id),
                'first': str(count),
                'after': str(max_id)
            }

            headers = self.generate_headers(self.user_session, self.__generate_gis_token(variables))

            response = self.__req.get(endpoints.get_account_medias_json_link(variables), headers=headers)

            if (Instagram.HTTP_OK != response.status_code):
                raise InstagramException.default(response.text, response.status_code)

            arr = json.loads(response.text)

            try:
                nodes = arr['data']['user']['edge_owner_to_timeline_media']['edges']
            except KeyError:
                return {}

            for mediaArray in nodes:
                if index == count:
                    return medias
                    
                media = Media(mediaArray['node'])
                medias.append(media)
                index += 1

            if nodes == None or nodes == '':
                return medias
            
            max_id = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            is_more_available = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

        return medias


    def get_media_by_id(self, media_id):
        '''
        param mediaId
     
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        media_link = Media.get_link_from_id(media_id)
        return self.get_media_by_url(media_link)

        
    def get_media_by_url(self, media_url):
        '''
        param string $mediaUrl
    
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        if len(re.findall(url_regex, media_url)) <= 0:
            raise ValueError('Malformed media url')

        url = media_url.rstrip('/') + '/?__a=1'
        response = self.__req.get(url, headers=self.generate_headers(self.user_session))
        
        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException('Media with given code does not exist or account is private.')

        if Instagram.HTTP_OK != response.status_code:
            raise InstagramException.default(response.text, response.status_code)

        media_array = response.json()
        try:
            mediaInJson = media_array['graphql']['shortcode_media']
        except KeyError:
            raise InstagramException('Media with this code does not exist')

        return Media(mediaInJson)


    def get_medias_from_feed(self, username, count = 20):
        '''
        param string username
        param int count
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
        medias = []
        index = 0
        response = self.__req.get(endpoints.get_account_json_link(username), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException('Account with given username does not exist.')

        if Instagram.HTTP_OK != response.status_code:
            raise InstagramException.default(response.text, response.status_code)

        user_array = response.json()

        try:
            user = user_array['graphql']['user']
        except KeyError:
            raise InstagramNotFoundException('Account with this username does not exist')
            
        try:
            nodes = user['edge_owner_to_timeline_media']['edges']
            if len(nodes) == 0:
                return []
        except:
            return []

        for media_array in nodes:
            if index == count:
                return medias
            medias.append(Media(media_array['node']))
            index += 1

        return medias
    

    def get_medias_by_tag(self, tag, count = 12, max_id = '', min_timestamp = None):
        '''
        param string $tag
        param int $count
        param string $maxId
        param string $minTimestamp
    
        return Media[]
        throws InstagramException
        '''
        index = 0
        medias = []
        media_ids = []
        has_next_page = True
        while index < count and has_next_page:

            response = self.__req.get(endpoints.get_medias_json_by_tag_link(tag, max_id),
                headers=self.generate_headers(self.user_session))

            if response.status_code != Instagram.HTTP_OK:
                raise InstagramException.default(response.text, response.status_code)

            arr = response.json()
           
            try:
                arr['graphql']['hashtag']['edge_hashtag_to_media']['count']
            except KeyError:
                return []
           
            nodes = arr['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            for media_array in nodes:
                if index == count:
                    return medias
                media = Media(media_array['node'])
                if media.identifier in media_ids:
                    return medias
                
                if min_timestamp != None and media.created_time < min_timestamp:
                    return medias

                media_ids.append(media.identifier)
                medias.append(media)
                index+=1

            if len(nodes) == 0:
                return medias
            
            max_id = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            has_next_page = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
            print('maxId:', max_id)
            print('hasNextPage:', has_next_page)

        return medias

        
    def get_medias_by_location_id(self, facebook_location_id, quantity = 24, offset = ''):
        '''
        param string facebookLocationId
        param int quantity
        param string offset
     
        return Media[]
        throws InstagramException
        '''

        index = 0
        medias = []
        has_next = True

        while index < quantity and has_next:

            response = self.__req.get(endpoints.get_medias_json_by_location_id_link(facebook_location_id, offset),
                headers=self.generate_headers(self.user_session))

            if response.status_code != Instagram.HTTP_OK:
                raise InstagramException.default(response.text,response.status_code)

            arr = response.json()

            nodes = arr['graphql']['location']['edge_location_to_media']['edges']
            for media_array in nodes:
                if index == quantity:
                    return medias

                medias.append(Media(media_array['node']))
                index += 1

            if len(nodes) == 0:
                return medias

            has_next_page = arr['graphql']['location']['edge_location_to_media']['page_info']['has_next_page']
            end_cursor = arr['graphql']['location']['edge_location_to_media']['page_info']['end_cursor']
            print(has_next_page, end_cursor)

        return medias

    def get_current_top_medias_by_tag_name(self, tag_name):
        '''
        param $tagName
     
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''

        response = self.__req.get(endpoints.get_medias_json_by_tag_link(tag_name, ''),
            headers=self.generate_headers(self.user_session))

        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (response.status_code != Instagram.HTTP_OK):
            raise InstagramException.default(response.text, response.status_code)


        json_response = response.json()
        medias = []

        nodes = json_response['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges']
        
        for media_array in nodes:
            medias.append(Media(media_array['node']))

        return medias

    def get_current_top_medias_by_location_id(self, facebook_location_id):
        '''
        param facebookLocationId
     
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = self.__req.get(endpoints.get_medias_json_by_location_id_link(facebook_location_id),
            headers=self.generate_headers(self.user_session))
        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException("Location with this id doesn't exist")

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()
        #print(response.json())
        nodes = json_response['graphql']['location']['edge_location_to_top_posts']['edges']
        medias = []

        for media_array in nodes:
            medias.append(Media(media_array['node']))

        return medias

    def get_paginate_medias(self, username, max_id = ''):
        '''
        param string username
        param string maxId
    
        return array
        throws InstagramException
        throws InstagramNotFoundException
        '''

        account = self.get_account(username)
        has_next_page = True
        medias = []

        toReturn = {
            'medias' : medias,
            'maxId' : max_id,
            'hasNextPage' : has_next_page,
        }

        variables = json.dumps({
            'id' : str(account.identifier),
            'first' : str(endpoints.request_media_count),
            'after' : str(max_id)
        })

        response = self.__req.get(
            endpoints.get_account_medias_json_link(variables),
            headers=self.generate_headers(self.user_session, self.__generate_gis_token(variables))
        )

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        arr = response.json()

        try: 
            nodes = arr['data']['user']['edge_owner_to_timeline_media']['edges']
        except KeyError:
            return toReturn

        #if (count($arr['items']) === 0) {
        # I generally use empty. Im not sure why people would use count really - If the array is large then count takes longer/has more overhead.
        # If you simply need to know whether or not the array is empty then use empty.
        for mediaArray in nodes:
            medias.append(Media(mediaArray['node']))


        end_cursor = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        has_next_page = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

        toReturn = {
            'medias' : medias,
            'maxId' : max_id,
            'hasNextPage' : has_next_page,
        }

        return toReturn

    def getPaginateMediasByTag(self, tag, max_id = ''):
        '''
        param string tag
        param string maxId
     
        return array
        throws InstagramException
        '''
        has_next_page = True
        medias = []

        to_return = {
            'medias' : medias,
            'maxId' : max_id,
            'hasNextPage' : has_next_page,
        }

        response = self.__req.get(endpoints.get_medias_json_by_tag_link(tag, max_id),
            headers=self.generate_headers(self.user_session))

        if response.status_code != Instagram.HTTP_OK :
            raise InstagramException.default(response.text, response.code)

        arr = response.json

        try:
            media_count = arr['graphql']['hashtag']['edge_hashtag_to_media']['count']
        except KeyError:
            return to_return

        try:
            nodes = arr['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        except KeyError:
            return to_return
        
        for media_array in nodes:
            medias.append(Media(media_array['node']))


        max_id = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        has_next_page = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        count = arr['graphql']['hashtag']['edge_hashtag_to_media']['count']

        to_return = {
            'medias' : medias,
            'count' : count,
            'maxId' : max_id,
            'hasNextPage' : has_next_page,
        }

        return to_return


    def get_location_by_id(self, facebook_location_id):
        '''
        param string $facebookLocationId
     
        return Location
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = self.__req.get(endpoints.get_medias_json_by_location_id_link(facebook_location_id),
            headers=self.generate_headers(self.user_session))

        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException('Location with this id doesn\'t exist')

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)
            
        json_response = response.json()

        return Location(json_response['graphql']['location'])

    def get_media_likes_by_code(self, code, count = 10, max_id = None):
        '''
        param      code
        param int count
        param null maxId
     
        return array
        throws InstagramException
        '''
        pass
        #TODO implement
        # remain = count
        # likes = []
        # index = 0
        # hasPrevious = True
        # #TODO: $index < $count (bug index getting to high since max_likes_per_request gets sometimes changed by instagram)
        # while (hasPrevious and index < count):
        #     if (remain > self.MAX_LIKES_PER_REQUEST):
        #         numberOfLikesToRetreive = self.MAX_LIKES_PER_REQUEST
        #         remain -= self.MAX_LIKES_PER_REQUEST
        #         index += self.MAX_LIKES_PER_REQUEST
        #     else:
        #         numberOfLikesToRetreive = remain
        #         index += remain
        #         remain = 0
            
        #     if (maxId != None):
        #         maxId = ''

        #     commentsUrl = endpoints.getLastLikesByCode(code, numberOfLikesToRetreive, maxId)
        #     response = self.__req.get(commentsUrl, headers=self.generateHeaders(self.userSession))

        #     if (response.status_code != Instagram.HTTP_OK):
        #         raise InstagramException(f'Response code is {response.status_code}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

        #     jsonResponse = response.json()
        #     print(jsonResponse)
        #     exit()

        #     $nodes = $jsonResponse['data']['shortcode_media']['edge_liked_by']['edges'];

        #     foreach ($nodes as $likesArray) {
        #         $likes[] = Like::create($likesArray['node']);
        #     }

        #     $hasPrevious = $jsonResponse['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page'];
        #     $numberOfLikes = $jsonResponse['data']['shortcode_media']['edge_liked_by']['count'];
        #     if ($count > $numberOfLikes) {
        #         $count = $numberOfLikes;
        #     }
        #     if (sizeof($nodes) == 0) {
        #         return $likes;
        #     }
        #     $maxId = $jsonResponse['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor'];

        # data['next_page'] = maxId
        # data['likes'] = likes

        # return data

    def get_followers(self, account_id, count = 20, page_size = 20, end_cursor = '', delayed = True):
        #TODO implement
        #previous method of extracting this data not working any longer
        '''
        param string accountId Account id of the profile to query
        param int count Total followers to retrieve
        param int pageSize Internal page size for pagination
        param bool delayed Use random delay between self.__req to mimic browser behaviour
     
        return array
        throws InstagramException
        '''
        #TODO set time limit
        # if ($delayed) {
        #     set_time_limit($this->pagingTimeLimitSec);
        # }

        index = 0
        accounts = []

        next_page = None

        if count < page_size:
            raise InstagramException('Count must be greater than or equal to page size.')

        while (True):
            next_page = None
            print(self.is_logged_in(self.user_session))
            response = self.__req.get(endpoints.get_followers_json_link(account_id, page_size, end_cursor),
                headers=self.generate_headers(self.user_session))

            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)

            
            jsonResponse = response.json()
            #TODO request gives empty response, fix
            print(jsonResponse)

            if (jsonResponse['data']['user']['edge_followed_by']['count'] == 0):
                return accounts

            edgesArray = jsonResponse['data']['user']['edge_followed_by']['edges']
            if len(edgesArray) == 0:
                InstagramException(f'Failed to get followers of account id {account_id}. The account is private.', Instagram.HTTP_FORBIDDEN)

            exit()
            pageInfo = jsonResponse['data']['user']['edge_followed_by']['page_info']
            if pageInfo['has_next_page']:
                next_page = pageInfo['end_cursor']
            for edge in edgesArray:
                accounts.append(edge['node'])
                index += 1
                if index >= count:
                    pass
                    #TODO does not work in python
                    #break 2

            # $pageInfo = $jsonResponse['data']['user']['edge_followed_by']['page_info'];
            # if ($pageInfo['has_next_page']) {
            #     $endCursor = $pageInfo['end_cursor'];
            # } else {
            #     break;
            # }

            # if ($delayed) {
            #     # Random wait between 1 and 3 sec to mimic browser
            #     $microsec = rand($this-> Microsec, $this->pagingDelayMaximumMicrosec);
            #     usleep($microsec);
            # }

        # $data['next_page'] = $next_page;
        # $data['accounts'] = $accounts;

        # return $data;


    def get_following(self, account_id, count = 20, page_size = 20, end_cursor = '', delayed = True):
        '''
        param string $accountId Account id of the profile to query
        param int $count Total followed accounts to retrieve
        param int $pageSize Internal page size for pagination
        param bool $delayed Use random delay between self.__req to mimic browser behaviour
     
        return array
        throws InstagramException
        '''
        pass
        #TODO implement
        #previous method of extracting this data not working any longer

    # {
    #     if ($delayed) {
    #         set_time_limit($this->pagingTimeLimitSec);
    #     }

    #     $index = 0;
    #     $accounts = [];

    #     $next_page = null;

    #     if ($count < $pageSize) {
    #         throw new InstagramException('Count must be greater than or equal to page size.');
    #     }

    #     while (true) {
    #         $next_page = null;

    #         $response = Request::get(endpoints::getFollowingJsonLink($accountId, $pageSize, $endCursor),
    #             $this->generateHeaders($this->userSession));

    #         if ($response->code !== static::HTTP_OK) {
    #             throw new InstagramException('Response code is ' . $response->code . '. Body: ' . static::getErrorBody($response->body) . ' Something went wrong. Please report issue.', $response->code);
    #         }

    #         $jsonResponse = $this->decodeRawBodyToJson($response->raw_body);

    #         if ($jsonResponse['data']['user']['edge_follow']['count'] === 0) {
    #             return $accounts;
    #         }

    #         $edgesArray = $jsonResponse['data']['user']['edge_follow']['edges'];
    #         if (count($edgesArray) === 0) {
    #             throw new InstagramException('Failed to get followers of account id ' . $accountId . '. The account is private.', static::HTTP_FORBIDDEN);
    #         }

    #         $pageInfo = $jsonResponse['data']['user']['edge_follow']['page_info'];
    #         if ($pageInfo['has_next_page']) {
    #             $next_page = $pageInfo['end_cursor'];
    #         }

    #         foreach ($edgesArray as $edge) {
    #             $accounts[] = $edge['node'];
    #             $index++;
    #             if ($index >= $count) {
    #                 break 2;
    #             }
    #         }

    #         $pageInfo = $jsonResponse['data']['user']['edge_follow']['page_info'];
    #         if ($pageInfo['has_next_page']) {
    #             $endCursor = $pageInfo['end_cursor'];
    #         } else {
    #             break;
    #         }

    #         if ($delayed) {
    #             # Random wait between 1 and 3 sec to mimic browser
    #             $microsec = rand($this->pagingDelayMinimumMicrosec, $this->pagingDelayMaximumMicrosec);
    #             usleep($microsec);
    #         }
    #     }

    #     $data['next_page'] = $next_page;
    #     $data['accounts'] = $accounts;

    #     return $data;
    # }

    def get_media_comments_by_id(self, media_id, count = 10, max_id = None):
        '''
        param mediaId
        param int count
        param null maxId
     
        return Comment[]
        throws InstagramException
        '''
        code = Media.get_code_from_id(media_id)
        return self.get_media_comments_by_code(code, count, max_id)


    def get_media_comments_by_code(self, code, count = 10, max_id = ''):
        #TODO implement not working!
        '''
        param      $code
        param int $count
        param null $maxId
     
        return Comment[]
        throws InstagramException
        '''
        comments = []
        index = 0
        has_previous = True

        while has_previous and index < count:

            if count - index > Instagram.MAX_COMMENTS_PER_REQUEST:
                number_of_comments_to_receive = Instagram.MAX_COMMENTS_PER_REQUEST
            else:
                number_of_comments_to_receive = count - index


            variables = json.dumps({
                'shortcode' : str(code),
                'first' : str(number_of_comments_to_receive),
                'after' : str(max_id)
            })

            comments_url = endpoints.get_comments_before_comments_id_by_code(variables)
            print(comments_url)
            response = self.__req.get(comments_url, headers=self.generate_headers(self.user_session, self.__generate_gis_token(variables)))
            # use a raw constant in the code is not a good idea!!
            #if ($response->code !== 200) {
            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)

            jsonResponse = response.json()
            print(jsonResponse)
            exit()
            # nodes = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['edges'];
 
            # foreach ($nodes as $commentArray) {
            #     $comments[] = Comment::create($commentArray['node']);
            #     $index++;
            # }
            # $hasPrevious = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['page_info']['has_next_page'];

            # $numberOfComments = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['count'];
            # if ($count > $numberOfComments) {
            #     $count = $numberOfComments;
            # }
            # if (sizeof($nodes) == 0) {
            #     return $comments;
            # }
            # $maxId = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['page_info']['end_cursor'];

        # $data['next_page'] = $maxId;
        # $data['comments'] = $comments;
        # return $data;

    def get_account(self, username):
        '''
        param string $username

        return Account
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = self.__req.get(endpoints.get_account_page_link(
            username), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException(
                'Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        user_array = Instagram.extract_shared_data_from_body(response.text)

        if user_array['entry_data']['ProfilePage'][0]['graphql']['user'] == None:
            raise InstagramNotFoundException('Account with this username does not exist')

        return Account(user_array['entry_data']['ProfilePage'][0]['graphql']['user'])


    def get_stories(self, reel_ids = None):
        '''
        param array reel_ids - array of instagram user ids
        return array
        throws InstagramException
        '''

        variables = {'precomposed_overlay' : False, 'reel_ids' : []}

        if reel_ids == None or len(reel_ids) == 0:
            response = self.__req.get(endpoints.get_user_stories_link(),
                headers=self.generate_headers(self.user_session))

            if (Instagram.HTTP_OK != response.status_code):
                raise InstagramException.default(response.text, response.status_code)

            json_response = response.json()

            try:
                edges = json_response['data']['user']['feed_reels_tray']['edge_reels_tray_to_reel']['edges']
            except KeyError:
                return []

            for edge in edges:
                variables['reel_ids'].append(edge['node']['id'])
        
        else:
            variables['reel_ids'] = reel_ids

        response = self.__req.get(endpoints.get_stories_link(variables),
            headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        try: 
            reels_media = json_response['data']['reels_media']
            if len(reels_media) == 0:
                return []
        except KeyError:
            return []

        stories = []
        for user in reels_media:
            user_stories = UserStories()

            user_stories.owner = Account(user['user'])
            for item in user['items']:
                story = Story(item)
                user_stories.stories.append(story)

            stories.append(user_stories)
        return stories

    def search_accounts_by_username(self, username):
        '''
        param string username
     
        return Account[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
    
        response = self.__req.get(endpoints.get_general_search_json_link(username), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        try:
            status = json_response['status']
            if status != 'ok':
                raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')
        except KeyError:
            raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')

        try: 
            users = json_response['users']
            if len(users)==0:
                return []
        except KeyError:
            return []

        accounts = []
        for json_account in json_response['users']:
            accounts.append(Account(json_account['user']))

        return accounts


     #TODO not optimal seperate http call after getMedia
    def get_media_tagged_users_by_code(self, code):
        '''
        param $code
     
        return array
        throws InstagramException
        '''
        url = endpoints.get_media_json_link(code)

        response = self.__req.get(url, headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        try: 
            tag_data = json_response['graphql']['shortcode_media']['edge_media_to_tagged_user']['edges']
        except KeyError:
            return []
        
        tagged_users = []

        for tag in tag_data:
            x_pos = tag['node']['x']
            y_pos = tag['node']['y']
            user = tag['node']['user']
            #TODO: add Model and add Data to it instead of Dict
            tagged_user = {}
            tagged_user['x_pos'] = x_pos
            tagged_user['y_pos'] = y_pos
            tagged_user['user'] = user

            tagged_users.append(tagged_user)
            
        
        return tagged_users

    def is_logged_in(self, session):
        '''
        param $session
   
        return bool
        '''
        if session == None or not 'sessionid' in session.keys():
            return False

        session_id = session['sessionid']
        csrf_token = session['csrftoken']

        headers = {
            'cookie' : f"ig_cb=1; csrftoken={csrf_token}; sessionid={session_id};",
            'referer' : endpoints.BASE_URL + '/',
            'x-csrftoken' : csrf_token,
            'X-CSRFToken' : csrf_token,
            'user-agent' : self.user_agent,
        }

        response = self.__req.get(endpoints.BASE_URL, headers=headers)

        if (response.status_code != Instagram.HTTP_OK):
            return False
    
        cookies = response.cookies.get_dict()

        if cookies == None or not 'ds_user_id' in cookies.keys():
            return False

        return True


    def login(self, force = False, two_step_verificator = None):
        '''
        param bool $force
        param bool|TwoStepVerificationInterface $twoStepVerificator

        support_two_step_verification true works only in cli mode - just run login in cli mode - save cookie to file and use in any mode
    
        throws InstagramAuthException
        throws InstagramException
    
        return array
        '''
        
        if self.session_username == None or self.session_password == None:
            raise InstagramAuthException("User credentials not provided")

        if two_step_verificator == True:
            two_step_verificator = ConsoleVerification()

        session = json.loads(Instagram.instance_cache.get_saved_cookies()) if Instagram.instance_cache.get_saved_cookies() != None else None

        if force or not self.is_logged_in(session):
            response = self.__req.get(endpoints.BASE_URL)
            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)
            
            match = re.findall(r'"csrf_token":"(.*?)"', response.text)
            
            if len(match) > 0:
                csrfToken = match[0]

            cookies = response.cookies.get_dict()

            # cookies['mid'] doesnt work at the moment so fetch it with function
            mid = self.__get_mid()

            headers = {
                'cookie' : f"ig_cb=1; csrftoken={csrfToken}; mid={mid};",
                'referer' : endpoints.BASE_URL + '/',
                'x-csrftoken' : csrfToken,
                'X-CSRFToken' : csrfToken,
                'user-agent' : self.user_agent,
            }
            payload = {'username' : self.session_username, 'password': self.session_password}
            response = self.__req.post(endpoints.LOGIN_URL, data=payload,headers=headers)
            
            if (response.status_code != Instagram.HTTP_OK):
                if (
                    response.status_code == Instagram.HTTP_BAD_REQUEST
                    and response.text != None
                    and response.json()['message'] == 'checkpoint_required'
                    and two_step_verificator != None):
                    response = self.__verify_two_step(response, cookies, two_step_verificator)
                    print('checkpoint required')
                
                elif response.status_code != None and response.text != None:
                    raise InstagramAuthException(f'Response code is {response.status_code}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)
                else:
                    raise InstagramAuthException('Something went wrong. Please report issue.', response.status_code)

            if not response.json()['authenticated']:
                raise InstagramAuthException('User credentials are wrong.')


            cookies = response.cookies.get_dict()

            cookies['mid'] = mid
            Instagram.instance_cache.set_saved_cookies(json.dumps(cookies))

            self.user_session = cookies

        else:
            self.user_session = session

        return self.generate_headers(self.user_session)


    def __verify_two_step(self, response, cookies, two_step_verificator):
        '''
        param response
        param cookies
        param TwoStepVerificationInterface $twoStepVerificator
        return Unirest\Response
        throws InstagramAuthException
        '''

        new_cookies =  response.cookies.get_dict()
        cookies = {**cookies, **new_cookies}
        
        cookie_string = ''
        for key in cookies.keys():
            cookie_string += f'{key}={cookies[key]};'

        headers = {
            'cookie' : cookie_string,
            'referer' : endpoints.LOGIN_URL,
            'x-csrftoken' : cookies['csrftoken'],
            'user-agent' : self.user_agent,
        }

        url = endpoints.BASE_URL + response.json()['checkpoint_url']

        response = self.__req.get(url, headers=headers)
        data = Instagram.extract_shared_data_from_body(response.text)

        if data != None:
            try:
                choices = data['entry_data']['Challenge'][0]['extraData']['content'][3]['fields'][0]['values']
            except KeyError:
                try:
                    fields = data['entry_data']['Challenge'][0]['fields']
                    try:
                        choice = {'label' : f"Email: {fields['email']}", 'value': 1}
                        choices = {**choices, **choice}
                    except KeyError:
                        pass
                    try:
                        choice = {'label' : f"Phone: {fields['phone_number']}", 'value' : 0}
                        choices = {**choices, **choice}
                    except KeyError:
                        pass

                except KeyError:
                    pass

            if len(choices) > 0:
                selected_choice = two_step_verificator.get_verification_type(choices)
                response = self.__req.post(url, data={'choice' : selected_choice}, headers=headers)
            
        
        if len(re.findall('name="security_code"',response.text)) <= 0:
            raise InstagramAuthException('Something went wrong when try two step verification. Please report issue.', response.status_code)

        security_code = two_step_verificator.get_security_code()

        post_data = {
            'csrfmiddlewaretoken' : cookies['csrftoken'],
            'verify' : 'Verify Account',
            'security_code' : security_code,
        }
        response = self.__req.post(url, data=post_data, headers=headers)
        if response.status_code != Instagram.HTTP_OK or 'Please check the code we sent you and try again' in response.text:
            raise InstagramAuthException('Something went wrong when try two step verification and enter security code. Please report issue.', response.status_code)

        return response
    

    def add_comment(self, media_id, text, replied_to_comment_id = None):
        '''
        param int|string|Media $mediaId
        param int|string $text
        param int|string|Comment|null $repliedToCommentId
     
        return Comment
        throws InstagramException
        '''
        media_id = media_id.identifier if isinstance(media_id, Media) else media_id
        
        replied_to_comment_id = replied_to_comment_id._data['id'] if isinstance(replied_to_comment_id, Comment) else replied_to_comment_id

        body = {'comment_text' : text, 'replied_to_comment_id' : replied_to_comment_id if replied_to_comment_id != None else ''}

        response = self.__req.post(endpoints.get_add_comment_url(media_id), data=body, headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        if json_response['status'] != 'ok':
            status = json_response['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

        return Comment(json_response)


    def delete_comment(self, media_id, comment_id):
        '''
        param string|Media $mediaId
        param int|string|Comment $commentId
        return void
        throws InstagramException
        '''
        media_id = media_id.identifier if isinstance(media_id, Media) else media_id
        comment_id = comment_id._data['id'] if isinstance(comment_id, Comment) else comment_id

        response = self.__req.post(endpoints.get_delete_comment_url(media_id, comment_id), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        if json_response['status'] != 'ok':
            status = json_response['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

    def like(self, media_id):
        '''
        param int|string|Media $mediaId
     
        return void
        throws InstagramException
        '''
        media_id = media_id.identifier if isinstance(media_id, Media) else media_id
        response = self.__req.post(endpoints.get_like_url(media_id), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        if json_response['status'] != 'ok':
            status = json_response['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

    def unlike(self, media_id):
        '''
        param int|string|Media $mediaId
        return void
        throws InstagramException
        '''
        media_id = media_id.identifier if isinstance(media_id, Media) else media_id
        response = self.__req.post(endpoints.get_unlike_url(media_id), headers=self.generate_headers(self.user_session))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()

        if json_response['status'] != 'ok':
            status = json_response['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

    def follow(self, user_id, username=None):
        """ Send http request to follow """
        if self.is_logged_in(self.user_session):
            url = endpoints.get_follow_url(user_id)
            if username is None:
                username = self.get_username_by_id(user_id)
            try:
                follow = self.__req.post(url_follow, headers=self.generate_headers(self.user_session))
                if follow.status_code == Instagram.HTTP_OK:
                    return True
            except:
                raise InstagramException("Except on follow!")
        return False

    def unfollow(self, user_id, username=""):
        """ Send http request to unfollow """
        if self.is_logged_in(self.user_session):
            url_unfollow = endpoints.get_unfollow_url(user_id)
            try:
                unfollow = self.s.post(url_unfollow)
                if unfollow.status_code == Instagram.HTTP_OK:
                    return unfollow
            except:
                raise InstagramException("Exept on unfollow!")
        return False
