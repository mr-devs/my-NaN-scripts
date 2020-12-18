# Written by Christopher Torres-Lugo

import tweepy
import json
import sys
import pandas as pd
# csv file with one tweet id per line
file = sys.argv[1]
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
tweets = list(pd.read_csv(file, header=None, names=['tid'])['tid'].values)
for tweets_batch in range(0,len(tweets), 100):
    try:
      result = api.statuses_lookup(id_=tweets[tweets_batch:tweets_batch+100],
                                 include_entities='true',
                                 trim_user='false',
                                 tweet_mode="extended")
      with open('rehydrated_twts.json', 'a') as f:
        for tweet_object in result:
          json.dump(tweet_object._json, f, ensure_ascii=True)
          f.write('\n')
    except:
        pass