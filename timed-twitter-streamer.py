#!/usr/bin/env python3

# Import packages
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import argparse
import json
import requests
import os
import time
import sys
from datetime import datetime as dt



# Set CLI Arguments
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Initiate the parser
parser = argparse.ArgumentParser(
  description="Script to query and then download data from Moes Tavern. Script requests user input (based on the included command line flags) to build the query for Moe."
  )
# Add optional arguments
parser.add_argument(
  "-t", "--time", 
  metavar='Time',
  type = float,
  help="How many hours would you like your script to run? (integer > 0. 1 = one hour, .5 = half and hour, etc. )"
  )

# Read parsed arguments from the command line into "args"
args = parser.parse_args()

# Assign them to objects
t = args.time
time2run = (60**2 * t)



# Create Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_headers(bearer_token):
    """
    This function adds the bearer token into the POST header you will
    be sending. This allows your API calls to be properly authenticated.
    """
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    """
    This function retrieves the existing rules that are in place on 
    your stream. If there are no rules, it should return something 
    like:
    {"meta": {"sent": "2020-12-13T14:55:21.080Z"}}
    """
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    """
    This function simply deletes all stream rules.
    """
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

def set_rules(headers, all_rules):
    """
    This function adds the rules that you pass into the
    function onto your stream.
    """
    
    payload = {"add": all_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, time2run):
    """
    This function begins the filter stream.

    This will run until the connection breaks or is manually
    stopped.
    """
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=entities",
        headers=headers,
        stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )

    today = dt.strftime(dt.today(), "%Y-%m-%d")
    with open(f"streaming_data--{today}.json", "w") as f:

        try:

            # Set when stream should end
            t_end = time.time() + time2run 

            for response_line in response.iter_lines():

                if time.time() > t_end:
                    raise KeyboardInterrupt()
                if response_line:
                    json_response = json.loads(response_line)
                    f.write(f"{json.dumps(json_response)}\n")

        except KeyboardInterrupt:
            sys.exit("Script manually entered or the indicated time ran out.")

def another_rule():
    answer = None 
    while answer not in ("yes", "no"): 
        answer = input("\nWould you like to add another rule? (y/n)\n\nAnswer: ") 
        if answer == "y": 
             return True 
        elif answer == "n": 
             return False
        else: 
          print("\nPLEASE ENTER 'y' OR 'n'.")

def import_rules():
    """
    Function for the user to input their own matching rules.
    """
    print("""**************

      Please input your own matching rules for the Twitter stream.

      Details: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules

      **************
      """)

    time.sleep(1)

    # list to fill with all rules
    all_rules = []

    # Example rule: {"value": "#covid OR #vaccine lang:en -is:retweet", "tag": "original set"}

    # Set switch so that the user can keep entering in rules.
    switch = True

    while switch:
        # Get the rule and it's tag
        rule_input = input("\nInput your matching rule\n\nRule: ")
        tag_input = input("\nInput a label tag for that rul\n\nRule Tag: ")

        # Create the proper rule form for the stream
        rule = {"value" : rule_input, "tag" : tag_input}

        # Append the new rule the list
        all_rules.append(rule)

        # Ask the user if they want to add another rule.
        answer = another_rule()

        # If they don't, flip the switch to False
        if answer:
            pass
        else:
            switch = False
    
    # Then return the list of rules
    return all_rules


# Execute program.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    try:
        # Load bearer token into program
        bearer_token = os.environ.get("BEARER_TOKEN")
    except:
        sys.exit("\nERROR: You forgot to set your bearer token!\n\n Do this by running:  export 'BEARER_TOKEN'='<your_bearer_token>'")

    # Create header w/ bearer to authorize stream
    headers = create_headers(bearer_token)

    # Get existing rules set from any old streams
    rules = get_rules(headers, bearer_token)

    # Delete them
    delete = delete_all_rules(headers, bearer_token, rules)

    all_rules = import_rules()

    # Set the new rules
    set_rules(headers, all_rules)

    # Print them so the user knows what they're looking for...
    print("\nRULES:\n\n")
    for num, rule in enumerate(all_rules):
      print(f"{num + 1}.",rule.get("value"))
      print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # Start streamer
    get_stream(headers, time2run)

    # Let the folks know!
    print("\n\nStreaming tweets...\n\nPress ctrl-c to cancel it.")


