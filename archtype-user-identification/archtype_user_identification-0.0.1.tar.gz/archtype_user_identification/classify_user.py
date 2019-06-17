import pickle
import tweepy

from archtype_user_identification.token_extract import find_token
from archtype_user_identification.build_embedding import model
from archtype_user_identification.twitter_preprocess import get_tweet_by_handle

class classify_user:
    ''' 
    
    Archtype_user_identification model to predict the archtype for the twitter user looking all the post in twitter they made.

    parameters:
    -----------
    model_path: string
        The location of trained model's pickle file.
        Training can be done from train_model module of this package which requires location to store the pickle file.
    
    list_group: list
        The group of archtype types.
    
    API_KEYS: string
       Twitter provided API_KEYS
    
    API_SECRET_KEY: string
        Twitter provided API_SECRET_KEY.
    
    ACCESS_TOKEN: string
        Twitter provided ACCESS_TOKEN.

    ACCESS_TOKEN_SECRET: string
        Twitter provided ACCESS_TOKEN_SECRET.
    '''
    def __init__(self, model_path, list_group, API_KEYS, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
        ''' 
        Initializing parameters of class
        '''
        self.list_group = list_group
        self.API_KEYS = API_KEYS
        self.API_SECRET_KEY = API_SECRET_KEY
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.ACCESS_TOKEN_SECRET = ACCESS_TOKEN_SECRET

        if model_path is not None:
            with open(model_path, 'rb') as f:
                self.classifying_model = pickle.load(f)
        else:
            classifying_model = model


    def twitter_auth(self):
        ''' 
        Authentication with twitter using the API keys' provided during class initialization.
        '''
        auth = tweepy.OAuthHandler(self.API_KEYS, self.API_SECRET_KEY)
        auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        return api
    
    def find_class(self, text):
        ''''
        This function return the classes on which the twitter post
        belongs to 

        argument: 
        ----------
        text -> string
            pre-processed twitter post 
        
        returns the archtype of twitter user

        input: text of type string
        output: text of type string
        '''
        
        assert isinstance(text,str)
        

        tokens = find_token(text)

        if len(tokens) == 0:
            return 'empty'
        
        similar = []

        for compare in self.list_group:
            compare_with_all = []
            
            for token in tokens:
                try:
                    similarity = self.classifying_model.similarity(compare,token)
                    compare_with_all.append(similarity)
                except:
                    compare_with_all.append(-1)
            
            similar.append(sum(compare_with_all))

        if max(similar) > 0:
            max_index = similar.index(max(similar))
            return self.list_group[max_index]
        
        return 'other'

    def classify(self, handle_name):
        '''
        This funtion accepts the twitter handle do all the pre-processing and predict the archtype of user using model.

        arguments:
        ----------
        handle_name:
            twitter_handle
        '''
        api = self.twitter_auth()

        post = get_tweet_by_handle(handle_name)
        class_belong = self.find_class(post)

        return class_belong
