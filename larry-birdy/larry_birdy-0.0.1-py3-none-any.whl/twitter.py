import re
from birdy.twitter import UserClient

class RestAPI(UserClient):
    API = None

    def __init__(self, consumer_key, consumer_secret,
                 access_token=None, access_token_secret=None):

        super().__init__(consumer_key, consumer_secret,
                         access_token, access_token_secret)

        RestAPI.API = self

        api = self.api
        self.account = api.account
        self.search = api.search

    def verify_account_credentials(self, skip_status=False):
        return self.account.verify_credentials.get(skip_status=skip_status).data

    def search_tweets(self, q, result_type, lang, count, tweet_mode):
        results = self.search.tweets.get(q=q,
                                         result_type=result_type,
                                         lang=lang,
                                         count=count,
                                         tweet_mode=tweet_mode)

        data = results.data
        return data.statuses

    def check_friendship(self, source, target):
        return self.api.friendships.show.get(source_id=source.id,
                                             target_id=target.id
                                             ).data.relationship

    def retweet(self, tweet, trim_user=False):
        return self.api.statuses.retweet.post(id=tweet.id, trim_user=trim_user)


class Data(object):
    def this(self, user=None, status=None):
        self.user = user
        self.status = status

        return self

    def extract_element_nodes_from(self, path):
        self.element_nodes = re.findall(r'\w+', path)

    def element(self, element):
        self.element_path = PathTo.element(element)
        return self

    def from_(self, status):
        data = status
        self.extract_element_nodes_from(self.element_path)
        for element in self.element_nodes:
            if element in data:
                data = data[element]
                if data == None:
                    break
            else:
                data = None
                break

        return data

    def within(self, status):
        return self.from_(status)

class Does(Data):
    def have_element(self, element):
        return bool(self.element(element).from_(self.status))

    def follow(self, user):
        relationship_data = RestAPI.API.check_friendship(source=self.user,
                                             target=user)
        return relationship_data.source.following

class Is(Data):
    def following(self, user):
        return Does.follow(self, user)

    def followed_by(self, user):
        relationship_data = RestAPI.API.check_friendship(source=self.user,
                                             target=user)
        return relationship_data.target.following

class Get(Data):
    pass

class Find(Data):
    def for_element(self, element):
        return self.element(element)

    def its_number_within(self, status):
        return len(self.within(status))


class p(object):
    pass

p.Does = Does()
p.Is = Is()
p.Get = Get()
p.Find = Find()

class PathTo(object):
    element_path = {
        'user_mentions': 'entities/user_mentions',
        'media': 'entities/media',
        'hashtags': 'entities/hashtags',
        'extended_media': 'extended_entities/media'
    }

    def element(element):
        return PathTo.element_path[element]
