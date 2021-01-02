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

DEPENDENCIES:
    - Tweepy (https://www.tweepy.org/)

Author: Matthew R. DeVerna
Date: 12/29/2020

CHANGELOG:
    - 01/02/2020: Removed the scripts use of emailer.py
    email updating system functionality to simplify the
    script.

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
  description="Scrape real-time tweets from Twitter using the V1 API based on keywords passed via file."
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
    """

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

        else:
            logging.info(f"Creating file: {file_name}")

            with open(file_name, "a+") as f:
                f.write(f"{data}")

        return True



    def on_error(self, status_code):
        # Log error with exception info
        logging.error(f"Error, code {status_code}", exc_info=True) 
        if status_code == 420:

            # Wait five minutes
            time.sleep(300)
            return True



def load_terms(file):
    logging.info("Attempting to load filter rules...")

    filter_terms = []
    with open(file, "r") as f:
        for line in f:
            logging.info("Loaded Filter Rule: {}".format(line.strip('\n')))
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
    listener = Listener()
    auth = OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    # Begin the stream.
    logging.info("Starting the stream...")
    while True:
        try:
            stream.filter(track=filter_terms, languages=["en"])
        except KeyboardInterrupt:
            logging.info("User manually ended stream with a Keyboard Interruption.")
            sys.exit("\n\nUser manually ended stream with a Keyboard Interruption.\n\n")
        except Exception as e:
            logging.debug('Unexpected exception: %s %e')
            continue