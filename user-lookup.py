#!/usr/bin/env python3

# Script Information
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
Purpose: Script to scrape Twitter users account information with Twitters V2 user_lookup endpoint
Author: Matthew DeVerna
Date: Dec. 17th 2020
"""


# Import packages
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import argparse
import requests
import os
import json
import pause
from tqdm import tqdm
from datetime import datetime as dt
from requests_oauthlib import OAuth1Session



# Set CLI Arguments.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Initiate the parser
parser = argparse.ArgumentParser(
    description="Script to scrape Twitter users account information."
)
# Add optional arguments
parser.add_argument(
    "-f", "--file",
    metavar='File',
    help="Full path to the file containing the USER IDS you would like to scrape."
)

# Read parsed arguments from the command line into "args"
args = parser.parse_args()

# Assign them to objects
file = args.file
# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'



# Create Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def auth():
    """A function which creates an oauth 
    object that we call Twitter with."""

    # Place user API keys here.
    consumer_key        = "VvIkzmSTHQtZWW6Map6qUTpEJ"
    consumer_secret     = "BpAnC8ejOOZgjBwG0DexQNdBiia259UNmS7yUfQbGpN8z0T0uZ"
    access_token        = "1312850357555539972-tuIRugj9vGuIceDnajSSEqmA4zTSP2"
    access_token_secret = "tsiBH8gLTAaf2TDBGcZXmtmUOAU3XpZMqUQjBhIJ8WIsj"

    # Get oauth object
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )
    return oauth


def create_params(userids):
    # You can enter up to 100 comma-separated user ID values.
        # E.g., "usernames=userid_1,userid_2,...,userid_100"
    
    # All user object fields included
    #   For more details, visit here: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user

    fields = "created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld"
    params = {"ids": userids, "user.fields": fields}
    
    return params


def connect_to_endpoint(oauth, params):
    """Downloads data from Twitter based on the `oauth` object passed and the
    `params` created with the `create_params()` function. 

    If time-dependent errors (429, 500, 503)

    """
    
    switch = True
    
    while switch:
        response = oauth.get("https://api.twitter.com/2/users", params=params)
        
        # Get number of requests left with our tokens
        remaining_requests = int(response.headers["x-rate-limit-remaining"])
        
        # If that number is one, we get the reset-time and wait until then, plus 15 seconds.
        # This is caught below as well, however, we want to program defensively, if possible.
        if remaining_requests == 1:
            buffer_wait_time = 15 
            resume_time = dt.fromtimestamp( int(response.headers["x-rate-limit-reset"]) + buffer_wait_time )
            print(f"Waiting on Twitter.\n\tResume Time: {resume_time}")
            pause.until(resume_time)

        """To be safe, we check explicitly for these TIME DEPENDENT errors.
        That is, these errors can be solved simply by waiting a little while 
        and pinging Twitter again. So that's what we do."""
        if response.status_code != 200:

            # Too many requests error
            if response.status_code == 429:
                buffer_wait_time = 15 
                resume_time = dt.fromtimestamp( int(response.headers["x-rate-limit-reset"]) + buffer_wait_time )
                print(f"Waiting on Twitter.\n\tResume Time: {resume_time}")
                pause.until(resume_time)

            # Twitter internal server error
            elif response.status_code == 500:
                # Twitter needs a break, so we wait 30 seconds
                resume_time = dt.now().timestamp() + 30
                print(f"Waiting on Twitter.\n\tResume Time: {resume_time}")
                pause.unit(resume_time)

            # Twitter service unavailable error
            elif response.status_code == 503:
                # Twitter needs a break, so we wait 30 seconds
                resume_time = dt.now().timestamp() + 30
                print(f"Waiting on Twitter.\n\tResume Time: {resume_time}")
                pause.unit(resume_time)

            # If we get this far, we've done something wrong and should exit
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        
        # If we get a 200 response, lets exit the function and return the response.json
        if response.ok:
            return response.json()


def chunker(seq, size):
    # A function which turns one list into a list of many lists that
    # are of length `size` or shorter (the last one)
        # This returns a GENERATOR for iteration
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def load_users(file):
    # Load all users, return a list of lists, each 100 
    # users long.
    #   This allows us to iterate through a long list of users
    # 100 users at a time (which is the maximum number of ids
    # we can query Twitter for in one call).
    with open(file, 'r') as f:
        users = [x.strip('\n') for x in f.readlines()]

    max_query_length = 100
    chunked_user_list = list(chunker(users, max_query_length))
    return chunked_user_list


def main():
    
    # Authorize API and return `oauth` object
    oauth = auth()

    # Get chunked list of 
    list_of_user_lists = load_users(file)

    # Get today's date
    today = dt.strftime(dt.today(), "%Y-%m-%d_%H-%M")

    # Open two files. One for good data, the other for account errors.
    with open(f"account_data--{today}.json", 'w') as data_file, open(f"account_errors--{today}.json", 'w') as error_file:

        # Iterate through the list of lists, starting a tqdm timer
        for one_hundred_users in tqdm(list_of_user_lists):
            stringify_list = ",".join(one_hundred_users)
            params = create_params(userids = stringify_list)
            json_response = connect_to_endpoint(oauth, params)
            data = json_response.get("data")
            errors = json_response.get("errors")
            data_file.writelines(f"{json.dumps(line)}\n" for line in data)
            try:
                error_file.writelines(f"{json.dumps(line)}\n" for line in errors)
            except TypeError:
                print("No problematic users found in this set of user, skipping to the next set.")
                pass

# Exectue the program
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    main()
    print("Data pull complete.")
