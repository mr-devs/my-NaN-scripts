#!/usr/bin/env python3

# Import packages
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import absolute_import, print_function
from tweepy import OAuthHandler, Stream, StreamListener
from datetime import datetime as dt
import argparse

# Set your Twitter tokens.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key=""
consumer_secret=""

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=""
access_token_secret=""



# Set CLI Arguments.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        today = dt.strftime(dt.today(), "%Y-%m-%d")
        with open(f"streaming_data--{today}.json", "a+") as f:
            f.write(f"{data}")
        return True

    def on_error(self, status):
        if status == 420:
            #returning False in on_error disconnects the stream
            return False




# Execute main program.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    # Set up the stream.
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    # Load File
    filter_terms = []
    with open(file, "r") as f:
        for line in f:
            filter_terms.append(line)

    # Begin the stream.
    stream.filter(track=filter_terms)
