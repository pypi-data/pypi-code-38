##IMPORTS
import dispy
import tweepy
import json
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
import argparse
myStream = None
def setUpTwitter(keysfile):
    ##SET UP TWITTER
    with open(keysfile) as f:
        keys = json.load(f)

    ## Or On Windows ##
    #with open (r'C:\Users\username\path_to\twitter_auth.json')
    #	keys = json.load(f)

    consumer_key = keys['consumer_key']
    consumer_secret = keys['consumer_secret']
    access_token = keys['access_token']
    access_token_secret = keys['access_token_secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api, consumer_key, consumer_secret, access_token, access_token_secret

tweets = []

##TWITTER STREAM
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        tweets.append(status.text.rstrip())
        print(("Tweet # %s" % (str(len(tweets)))))
        if len(tweets) > 200:
            myStream.disconnect()
def collect_tweets(api):
    global myStream
    pos_emojis = [chr(uni) for uni in [128537, 10084, 128525, 128147, 128535, 9786, 128522, 128539, 128149, 128512, 128515, 128538]]
    neg_emojis = [chr(uni) for uni in [9785, 128533, 128553, 128530, 128544, 128528, 128550, 128547, 128555, 128534, 128542, 128148, 128546, 128543]]
    all_emojis = pos_emojis + neg_emojis
    myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener())
    myStream.filter(track=all_emojis, languages=['en'])
    return pos_emojis, neg_emojis, all_emojis

def store_tweets(file, tweets):
    with open(file, 'r') as f:
        old_tweets = f.readlines()
    all_tweets = old_tweets + tweets
    all_tweets = list(set(all_tweets))
    all_tweets = [tweet.replace('\n','')+"\n" for tweet in all_tweets]
    all_tweets = [tweet.replace('\n','')+"\n" for tweet in all_tweets]
    with open(file, 'w') as f:
        f.writelines(all_tweets)
    return all_tweets
def clean_tweets(tweets):
    import re
    import string
    tweets = [re.sub(r'@\S+', '', tweet) for tweet in tweets]
    tweets = [re.sub(r'http\S+', '', tweet) for tweet in tweets]
    tweets = [tweet.translate({ord(char): ' ' for char in string.punctuation}) for tweet in tweets]
    tweets = [tweet.rstrip() for tweet in tweets]
    return list(tweets)
def sort_tweets(tweets, pos_emojis, neg_emojis):
    pos_tweets = [tweet for tweet in tweets if set(tweet) & set(pos_emojis)]
    neg_tweets = [tweet for tweet in tweets if set(tweet) & set(neg_emojis)]
    pos_tweets = [re.sub(r'[^\x00-\x7F]+','', tweet) for tweet in pos_tweets]
    neg_tweets = [re.sub(r'[^\x00-\x7F]+','', tweet) for tweet in neg_tweets]
    return pos_tweets, neg_tweets
def parse_tweets(words):
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    words = words.lower()
    words = word_tokenize(words)
    words = [word for word in words if word not in stopwords.words("english")]
    word_dictionary = dict([(word, True) for word in words])
    return word_dictionary
def train_classifier(positive_tweets, negative_tweets):
    import nltk.classify.util
    from nltk.classify import NaiveBayesClassifier
    positive_tweets = [(parse_tweets(tweet),'positive') for tweet in positive_tweets]
    negative_tweets = [(parse_tweets(tweet),'negative') for tweet in negative_tweets]
    fraction_pos =  round(len(positive_tweets) * 0.8)
    fraction_neg =  round(len(negative_tweets) * 0.8)

    train_set = negative_tweets[:fraction_pos] + positive_tweets[:fraction_pos]
    test_set =  negative_tweets[fraction_neg:] + positive_tweets[fraction_neg:]
    classifier = NaiveBayesClassifier.train(train_set)
    accuracy = nltk.classify.util.accuracy(classifier, test_set)
    return classifier, accuracy
def calculate_naughty(pos_tweets, neg_tweets, user, consumer_key, consumer_secret, access_token, access_token_secret):
    import tweepy
    import json
    import re
    import string
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    import nltk.classify.util
    from nltk.classify import NaiveBayesClassifier
    if "RT" in user or "@" in user:
        return "Couldn't calculate"
    elif " " in user:
        return "Couldn't calculate"
    else:
        try:

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            
            classifier, accuracy = train_classifier(pos_tweets, neg_tweets)
            user_tweets = api.user_timeline(screen_name = user ,count=200)
            user_tweets = [tweet.text for tweet in user_tweets]
            user_tweets = clean_tweets(user_tweets)
            rating = [classifier.classify(parse_tweets(tweet)) for tweet in user_tweets]
            fraction_tweets = round(len(rating) * 0.5)
            if rating.count('negative') > fraction_tweets:
                return "User: " + user + " is NAUGHTY! " + str(rating.count('negative')) + "  of " + str(len(rating)) + " tweets for this user are NAUGHTY! Accuracy: " + str(accuracy)
            else:
                return "User: " + user + " is NICE! " + str(rating.count('positive')) + "  of " + str(len(rating)) + " tweets for this user are NICE! Accuracy: " + str(accuracy)
        except Exception as e:
            return "Couldn't calculate, Exception: " + str(e)

def getUsers(tweets, all_emojis):
    users = [tweet.replace("\n", "") for tweet in tweets]
    users = [tweet.replace(" ", "") for tweet in users]
    users = [tweet.replace("RT@", "") for tweet in users]
    users = [re.sub(r':\S+', '', tweet) for tweet in users]
    print(("Found %s users" % (str(len(users)))))
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("showusers", type=str, help="Show Users(Y/n)")
        args = parser.parse_args()
        h = args.showusers
    except:
        while True:
            h = input("Do you want to show them? (Y/n) ")
            listOfInputs = ["no", "n", "y", "yes"]
            listOfInputs = listOfInputs + [i.upper() for i in listOfInputs]
            try:
                if h in listOfInputs:
                    break
                else:
                    raise RuntimeError
            except:
                print("Make sure your input is in this list:")
                for i in listOfInputs:
                    print(i)
                
    h = h.lower()
    usrnum = 1
    if h == "y" or h == "yes":
        print("Ok")
        found = False
        for i in users:
            for e in all_emojis:
                if set(e) & set(i):
                    print("Couldn't print user. Reason: Emoji detected")
                    found = True
            if found == False:
                try:
                    print(("User # %s: %s" % (str(usrnum), i)))
                except Exception as e:
                    print(str(e))
            else:
                found = False
            usrnum = usrnum + 1
    else:
        print("Ok")
    return users

##EXECUTE
class Calculate:
    def __init__(self, fileOfCredentialsPath):
        global tweets
        print("Getting tweets...")
        self._api, self._consumer_key, self._consumer_secret, self._access_token, self._access_token_secret = setUpTwitter(fileOfCredentialsPath)
        self._pos_emojis, self._neg_emojis, self._all_emojis = collect_tweets(self._api)
        print("Getting users")
        self._users = getUsers(tweets, self._all_emojis)
        print("Storing tweets")
        self._tweets = store_tweets('tweets.txt', tweets)
        print("Cleaning tweets")
        self._tweets = clean_tweets(self._tweets)
        print("Sorting tweets")
        self._pos_tweets, self._neg_tweets = sort_tweets(self._tweets, self._pos_emojis, self._neg_emojis)
        print("Calculating using your cluster")
        cluster = dispy.JobCluster(calculate_naughty, nodes='192.168.1.*', depends=[parse_tweets, clean_tweets, train_classifier])
        jobs = []
        id = 1
        for user in self._users:
            job = cluster.submit(self._pos_tweets, self._neg_tweets, user, self._consumer_key, self._consumer_secret, self._access_token, self._access_token_secret)
            job.id = id # Associate an ID to the job
            jobs.append(job)
            id += 1   # Next job
        print(("Doing %s jobs" % (str(len(jobs)))))
        print("Waiting")
        cluster.wait()
        print("Collecting job results")
        results = []
        for job in jobs:
            result = job()
            print(("Raspberry Pi %s did job %s at %s" % (job.ip_addr, job.id, job.start_time)))
            if result != None:
                results.append(result)
            else:
                print("There was an error while calculating")
                print("Error:")
                print(job.exception)
                cluster.print_status()
                cluster.close()
                raise RuntimeError("Couldn't calculate")
        print("Showing Results:")
        with open("results.txt", "a") as f:
            for result in results:
                print(result)
                f.writelines(result)
        cluster.print_status()
        cluster.close()
    def __repr__(self):
        return "Calculated"

