#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
# from flask.ext.pymongo import PyMongo
from twitter_fire_scraper.config import Config
from twitter_fire_scraper.scraper import Scraper
from twitter_fire_scraper.twitter import TwitterAuthentication
from twitter_fire_scraper.util import jsonify_status_dict, save_single_status_to_mongodb

app = Flask(__name__, static_url_path="/static")

app.config['MONGO_DBNAME'] = 'twitterfirescraperapi'  # name of your cluster
app.config['MONGO_URI'] = 'mongodb+srv://trungpham10:!twitterfire1@twitterfirescraperapi-i6mwc.mongodb.net/test?retryWrites=true'
# mongodb username and password here

mongo = PyMongo(app)

scraper = Scraper(twitter_authentication=TwitterAuthentication.autodetect_twitter_auth())


@app.route('/add_new', methods=['GET'])
def add():
    user = mongo.db.users
    user.insert_one({'city': 'New York'})
    return 'New York is added!'


@app.route('/scrape_terms', methods=['GET'])
def scrape_terms():
    # user1 = mongo.db.users

    print('scrape_terms')
    print(request.args)

    count = request.args.get("count")
    if not count:
        abort(400, "'count' is a required URL parameter!")

    try:
        count = int(count)

        if count < 0:
            raise ValueError
    except ValueError:
        abort(400, "'count' should be a valid number!")

    terms = request.args.get("terms")

    print(terms)

    if not terms:
        abort(400, "'terms' is a required URL parameter!")

    terms = terms.split(",")
    if len(terms) <= 0:
        abort(400, "'terms' cannot be an empty list!")

    geocode = request.args.get("geocode")

    results = (scraper.scrape_terms(terms=terms, count=count, geocode=geocode))  # dict object

    # user1.insert(results)

    results = jsonify_status_dict(results)  # json object

    return jsonify(results)
    # return jsonify("You want {} tweets for {}?".format(count, terms))


@app.route('/scrape_accounts', methods=['GET'])
def scrape_accounts():
    count = request.args.get("count")
    if not count:
        abort(400, "'count' is a required URL parameter!")
    try:
        count = int(count)
        if count < 0:
            raise ValueError
    except ValueError:
        abort(400, "'count' should be a valid number!")

    accounts = request.args.get("accounts")
    if not accounts:
        abort(400, "'accounts' is a required URL parameter!")
    accounts = accounts.split(",")
    if len(accounts) <= 0:
        abort(400, "'accounts' cannot be an empty list!")

    results = (scraper.scrape_accounts(accounts=accounts, count=count))

    results = jsonify_status_dict(results)

    return jsonify(results)
    # return jsonify("You want {} tweets for {}?".format(count, term))


@app.route('/scrape', methods=['GET'])
def scrape():
    count = request.args.get("count")
    if not count:
        abort(400, "'count' is a required URL parameter!")
    try:
        count = int(count)
        if count < 0:
            raise ValueError
    except ValueError:
        abort(400, "'count' should be a valid number!")

    terms = request.args.get("terms")
    if not terms:
        abort(400, "'terms' is a required URL parameter!")
    terms = terms.split(",")
    if len(terms) <= 0:
        abort(400, "'terms' cannot be an empty list!")

    accounts = request.args.get("accounts")
    if not accounts:
        abort(400, "'accounts' is a required URL parameter!")
    accounts = accounts.split(",")
    if len(accounts) <= 0:
        abort(400, "'accounts' cannot be an empty list!")

    geocode = request.args.get("geocode")

    results = (scraper.scrape(terms=terms, accounts=accounts, count=count, geocode=geocode))

    results = jsonify_status_dict(results)

    return jsonify(results)
    # return jsonify("You want {} tweets for {}?".format(count, term))


@app.route('/info', methods=['GET'])
def info():  # function: check webapi is running or not
    return "twitter-fire-scraper-webapi"


@app.route('/')
def index():
    return jsonify({'info': 'Welcome. This is the twitter-fire-scraper-webapi. This is a Web API, and not meant to be viewed in your browser.'})


@app.route('/add/<int:x>/<int:y>', methods=['GET'])
def add_numbers(x, y):
    return str(x + y)


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=Config.Defaults.API_PORT, debug=True)
