#!/usr/bin/env python3

"""
PURPOSE: 
    - To create a real-time FILTERED stream of Twitter
    data, utilizing the Twitter V1 API.

INPUT:
    - A file with keywords/hashtags (one per line) that
    will be utilized as the filters matching to tweets 
    in real-time.

OUTPUT:
    - One JSON file is created - per day - where each
    line item represents one tweet object. 

DEPENDENCY:
    - emailer.py should be kept in the same directory as
    this file.

Author: Matthew R. DeVerna
Date: 12/29/2020

"""

# Import packages
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys
import argparse
import logging
from datetime import datetime as dt

from tweepy import OAuthHandler, Stream, StreamListener
from emailer import eMessages, send_email
from email.mime.text import MIMEText



# Initialize the log
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

now = dt.strftime(dt.now(), '%m-%d-%Y_%H-%M-%S')
# Define file handler and set logger formatter
log_filename = f"{now}_stream.log"


logging.basicConfig(
    filename= log_filename,
    format='%(levelname)s - %(asctime)s | %(message)s',
    datefmt= "%m-%d-%Y_%H-%M-%S",
    level= logging.INFO)



# Set your Twitter tokens.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

logging.info("Loading Twitter API Keys/Tokens.")

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
api_key = os.environ.get("TWITTER_API_KEY")
api_key_secret = os.environ.get("TWITTER_API_KEY_SECRET")

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")



# Set CLI Arguments.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

logging.info("Parsing Command Line Arguments.")

# Initiate the parser
parser = argparse.ArgumentParser(
  description="Script to query and then download data from Moes Tavern. Script requests user input (based on the included command line flags) to build the query for Moe."
  )
# Add optional arguments
parser.add_argument(
  "-f", "--file", 
  metavar='File',
  help="Full path to the file containing terms you would like to include. (One object (i.e. hashtag) per line)"
  )

# Read parsed arguments from the command line into "args"
args = parser.parse_args()

# Assign them to objects
file = args.file



# Build Functions.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Listener(StreamListener):
    """ 
    A listener handles tweets that are received from the stream.
    This is a relatively basic listener that just writes to a filename
    labeled by the day it is created.
    """
    def __init__(
        self,
        time,
        log_filename,
        total_tweets,
        todays_tweets
        ):
        self._time = time
        self._log_filename = log_filename
        self._total_tweets = total_tweets
        self._todays_tweets = todays_tweets

    def on_data(self, data):
        today = dt.strftime(dt.now(), "%Y-%m-%d")
        file_name = f"data/streaming_data--{today}.json"

        """
        The 'if os.path.isfile()' line below checks if the data 
        file has already been created. If not, we send an email update
        which includes an update on the number of total tweets
        collected as well as the number of tweets collected that day.

        Since a new file will be created at the beginning of each day, 
        this if statement will only be activated once at the very end of
        of day.
        """
        if os.path.isfile(file_name):
            with open(file_name, "a+") as f:
                f.write(f"{data}")
                self._total_tweets += 1
                self._todays_tweets += 1

        else:
            logging.info("Sending daily email update...")
            e_message = eMessages(
                time = dt.strftime(dt.now(), "%Y-%m-%d"),
                log_filename = log_filename,
                total_tweets = self._total_tweets,
                todays_tweets = self._todays_tweets).daily_update()

            send_email(
                email_message = e_message,
                emailType = "daily_update"
                )

            self.todays_tweets = 0
            with open(file_name, "a+") as f:
                f.write(f"{data}")
                self._total_tweets += 1
                self._todays_tweets += 1

        return True

    def on_error(self, status):
        logging.error("Error, code {}".format(status))
        if status == 420:
            time.sleep(300)

def load_terms(file):
    logging.info("Attempting to load filter rules...")

    filter_terms = []
    with open(file, "r") as f:
        for line in f:
            filter_terms.append(line)

    return filter_terms



# Execute main program.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    # Create data dir if it doesn't exist already
    try:
        os.makedirs("data")
    except:
        pass

    # Loading the file terms...
    filter_terms = load_terms(file)

    # Set up the stream.
    logging.info("Setting up the stream...")
    listener = Listener(
        time = dt.strftime(dt.now(), '%m-%d-%Y_%H-%M-%S'),
        log_filename = log_filename,
        total_tweets = 0,
        todays_tweets = 0
        )
    auth = OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    # Begin the stream.
    logging.info("Starting the stream...")
    stream.filter(track=filter_terms)

