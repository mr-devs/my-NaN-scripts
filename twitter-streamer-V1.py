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

# Dependencies
from tweepy import OAuthHandler, Stream, StreamListener
from emailer import eMessages, send_email
from email.mime.text import MIMEText



# Initialize the log
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get current time
now = dt.strftime(dt.now(), '%m-%d-%Y_%H-%M-%S')

# Define file handler and set logger formatter
log_filename = f"{now}_stream.log"

# Set logging configuration
logging.basicConfig(
    filename= log_filename,
    format='%(levelname)s - %(asctime)s | %(message)s',
    datefmt= "%m-%d-%Y_%H-%M-%S",
    level= logging.INFO)



# Set your Twitter tokens.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logging.info(f"Script begins: {now}")
logging.info("Loading Twitter API Keys/Tokens...")

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

logging.info("Parsing Command Line Arguments...")

# Initiate the parser w. a simple description.
parser = argparse.ArgumentParser(
  description="Scrape real-time tweets from Twitter using the V1 API using based on keywords passed via file."
  )
# Add optional arguments
parser.add_argument(
  "-f", "--file", 
  metavar='File',
  help="Full path to the file containing keywords you would like to include. (One object (i.e. hashtag) per line)"
  )

# Read parsed arguments from the command line into "args"
args = parser.parse_args()

# Assign them to objects
file = args.file



# Build Functions.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Listener(StreamListener):
    """ 
    The Listener wraps tweepys StreamListener allowing customizable handling
    of tweets and errors received from the stream.
    
    This Listener does the following:
        - Writes raw tweet data to a file named for the day it is scraped.
        - Provides email updates at the end of each day.
        - Provides email updates when being rate limited by Twitter.
    """
    def __init__(
        self,
        time,
        log_filename,
        total_tweets,
        todays_tweets,
        rate_limits,
        ):
        self._time = time
        self._log_filename = log_filename
        self._total_tweets = total_tweets
        self._todays_tweets = todays_tweets
        self._rate_limits = rate_limits

    def on_data(self, data):
        today = dt.strftime(dt.now(), "%m-%d-%Y")
        file_name = f"data/streaming_data--{today}.json"

        """
        The 'if os.path.isfile()' line below checks if the data 
        file has already been created for a given day. If not, 
        we send an email update which includes an update on 
        the number of total tweets collected as well as the
        number of tweets collected that day.

        Since a new file will be created at the beginning of 
        each day, this if statement will only be activated 
        once at the very end of of day.

        This allows us to get updates on the volume of tweets 
        we are capturing and get an idea of when a surge
        may be taking place. 
        """
        if os.path.isfile(file_name):
            with open(file_name, "a+") as f:
                f.write(f"{data}")
                self._total_tweets += 1
                self._todays_tweets += 1
                self._rate_limits = 0

        else:
            logging.info("Sending daily email update...")
            # Create email update message
            e_message = eMessages(
                time = dt.strftime(dt.now(), "%m-%d-%Y_%H-%M-%S"),
                log_filename = log_filename,
                total_tweets = self._total_tweets,
                todays_tweets = self._todays_tweets).daily_update()

            # Send email
            send_email(
                email_message = e_message,  # Creates body of email
                emailType = "daily_update"  # Creates email subject
                )

            # Set todays tweet count to zero and write data.
            self.todays_tweets = 0

            logging.info(f"Creating file: {file_name}")

            with open(file_name, "a+") as f:
                f.write(f"{data}")
                self._total_tweets += 1
                self._todays_tweets += 1
                self._rate_limits = 0

        return True

    def on_error(self, status_code):
        # Log error with exception info
        logging.error(f"Error, code {status_code}", exc_info=True) 
        if status_code == 420:
            self._rate_limits += 1 

            logging.info("Waiting 300 seconds due to rate-limiting.")

            # Create rate limiting email message 
            e_message = eMessages(
                time = dt.strftime(dt.now(), "%Y-%m-%d"),
                log_filename = log_filename,
                rate_limits = self._rate_limits).rate_limit()

            # Send email
            send_email(
                email_message = e_message, # Creates body of email
                emailType = "rate_limit"   # Creates email subject
                )

            # Wait five minutes
            time.sleep(300)




def load_terms(file):
    logging.info("Attempting to load filter rules...")

    filter_terms = []
    with open(file, "r") as f:
        for line in f:
            logging.info(f"Loaded Filter Rule: {line.strip('\n')}")
            filter_terms.append(line.strip("\n"))

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
        todays_tweets = 0,
        rate_limits= 0
        )
    auth = OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    # Begin the stream.
    logging.info("Starting the stream...")
    while True:
        try:
            stream.filter(track=filter_terms)
        except KeyboardInterrupt:
            logging.info("User manually ended stream with a Keyboard Interruption.")
            sys.exit("\n\nUser manually ended stream with a Keyboard Interruption.\n\n")


