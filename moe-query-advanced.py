"""
This is a command line script to pull data from Moe's Tavern.

Simply call the script with the proper command line flags (see
options by calling "python3 moe-query-advanced.py -h") and the
script will walk you through the rest.

NOTES FROM MOE'S TAVERN!
The Moe's Tavern tool is available for research by Indiana University users only. 
All fields are required. You will receive an email with the results. 
Query results will be auto-deleted after a few days. All requests are logged. 
READ THESE NOTES CAREFULLY:
  - Data is available only for the past 36 months, so queries beginning before 36 
  months ago will fail.
  - Moe's Tavern returns at most 1 million tweet ids. If the number is exceeded,
  the results will be truncated. Check if the number of tweets matches the limit
  to determine if the results were truncated.
  - Sometimes, you might get out-of-memory errors from the query. The memory limit
  may depend on the combination of query load and cluster load. You will get an
  error if the memory limit is exceeded, shortly after the query is submitted.
  - If your job takes more than two hours, it will be killed. Check the error file
  (error.log) for details. If this happens, modify your query so that it will take
  less time.
  - Please beware that prior to 2020-08-12, entities (e.g., links and hashtags)
  in extended tweets were truncated.

Site Location: https://carl.cs.indiana.edu/moe/

"""


import argparse
import dateutil.parser
import requests
from bs4 import BeautifulSoup
import urllib.request
import pprint
import sys


pp = pprint.PrettyPrinter(indent = 4)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CLI ARGUMENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Initiate the parser
parser = argparse.ArgumentParser(
  description="Script to query and then download data from Moes Tavern. Script requests user input (based on the included command line flags) to build the query for Moe."
  )
# Add optional arguments
parser.add_argument(
  "-t", "--hashtags", 
  action='store_true',
  help="Find tweets containing a list of hashtags."
  )
parser.add_argument(
  "-u", "--urls", 
  action='store_true',
  help="Find tweets containing a list of urls."
  )
parser.add_argument(
  "-id", "--user_ids", 
  action='store_true',
  help="Find tweets sent by a list of numeric user ids."
  )
parser.add_argument(
  "-tc", "--tweet_content", 
  action='store_true',
  help="Return the full tweet object."
  )
parser.add_argument(
  "-ti", "--tweet_ids", 
  action='store_true',
  help="Return only the tweet_ids."
  )
parser.add_argument(
  "-f", "--file", 
  action='store_true',
  help="Use an input file in your query. File should have one query object (url, hashtag, or user id) per line."
  )

# Read parsed arguments from the command line into "args"
args = parser.parse_args()

# Assign them to objects
hashtags = args.hashtags
urls = args.urls
user_ids = args.user_ids
tweet_content = args.tweet_content
tweet_ids = args.tweet_ids
file = args.file

# Make sure something was passed.
if sum([hashtags, urls, user_ids, tweet_content, tweet_ids, file]) == 0:
  raise TypeError("No flags were passed. The script will now terminate.\n\nIndicate the data you'd like to pull by passing ONE of the following flags: -t, -u, -i.")

# Make sure only one query type was passed
if sum([hashtags, urls, user_ids]) != 1:
  raise TypeError("Can only pass ONE of the following flags: -t, -u, -i.")

# Make sure the requested returned data is of only one type.
if sum([tweet_content, tweet_ids]) != 1:
  raise TypeError("Can only pass ONE of the following flags: -tc, -ti.")




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SET FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def get_moes_url():
  get_moes_str = "Please visit the below website... \n\nhttps://carl.cs.indiana.edu/moe\n\n... and then take the url from the bottom of the page and enter it here.\n URL: "
  moes_url = input(get_moes_str)
  return moes_url


def load_file():
  file_path = input("**** Please input the full file_path containing your query objects below.\n")

  all_q_objects = []
  with open(file_path, "r") as f:
    for line in f:
      all_q_objects.append( line.rstrip("\n") )

  if len(all_q_objects) > 5000:
    raise TypeError("You have pass more than 5000 search queries in your file. This is too large for Moe's Tavern. Please chunk the file into multiple smaller files and resubmit individually.")

  else:
    return all_q_objects


def get_date_details():
  print("**** Input query start time and end time.\n")
  print("--> Start time and end time specify the time period over which to search.\n\n")

  start_time = input("Please input the START TIME\n\nExample: 2020-12-03T00:00\n\n~~~~~~~~~~")
  end_time = input("Please input the END TIME\n\nExample: 2020-12-03T00:00\n\n~~~~~~~~~~")

  start_time_dt = dateutil.parser.parse(start_time)
  end_time_dt = dateutil.parser.parse(end_time)

  if end_time_dt < start_time_dt:
    raise TypeError("The end time entered occurs before start time. Please try again.")

  else:
    return start_time, end_time


def create_query(qtype, data_type2return):

  email_query_help = "**** Input your Indiana University email address.\n\nEMAIL: "

  hashtag_query_help = "**** Input comma-separated list of hashtags (no spaces).\n\nNOTE: e.g. #truthy,#twitter. Note that for right-to-left languages such as Arabic, the '#' symbol should be placed on the left of the string in the query. Trailing wildcards are allowed e.g. #occupy*\n\n HASHTAGS: "
  urls_query_help = "**** Input comma-separated list of urls (no spaces).\n\nMust specify protocol and subdomains, and trailing wildcards are encouraged, e.g. http://cnn.com*, https://cnn.com*, http://m.cnn.com*, https://m.cnn.com*\n\nURLS: "
  user_ids_help = "**** Input numeric user IDs, comma-separated (no spaces):\n\nUSER IDS: "

  email = input(email_query_help)

  ### HASHTAGS ###

  if hashtags:
    if file:
      all_q_objects = load_file()
      all_q_objects = ["#" + obj for obj in all_q_objects]
      all_q_objects_one_str = ",".join(all_q_objects)
      start_time, end_time = get_date_details()

    else:
      all_q_objects = input(hashtag_query_help)
      all_q_objects = ["#" + obj for obj in all_q_objects]

      # If only one is entered, it is received as a string, so we don't 
      # need to do the join process below.
      if isinstance(all_q_objects,str) == False:
        all_q_objects_one_str = ",".join(all_q_objects)
      else:
        all_q_objects_one_str = all_q_objects

      start_time, end_time = get_date_details()

  ### URLS ###

  elif urls:
    if file:
      all_q_objects = load_file()
      all_q_objects_one_str = ",".join(all_q_objects)
      start_time, end_time = get_date_details()

    else:
      all_q_objects = input(urls_query_help)

      # If only one is entered, it is received as a string, so we don't 
      # need to do the join process below.
      if isinstance(all_q_objects,str) == False:
        all_q_objects_one_str = ",".join(all_q_objects)
      else:
        all_q_objects_one_str = all_q_objects

      start_time, end_time = get_date_details()

  ### USER IDS ###

  else:
    if file:
      all_q_objects = load_file()
      all_q_objects_one_str = ",".join(all_q_objects)
      start_time, end_time = get_date_details()

    else:
      all_q_objects = input(user_ids_help)

      # If only one is entered, it is received as a string, so we don't 
      # need to do the join process below.
      if isinstance(all_q_objects,str) == False:
        all_q_objects_one_str = ",".join(all_q_objects)
      else:
        all_q_objects_one_str = all_q_objects

      start_time, end_time = get_date_details()

  # Generate query dictionary
  query_details  = {
  "email": email,
  "qtype": qtype,
  "q": all_q_objects_one_str,
  "start": start_time,
  "end": end_time,
  "output": data_type2return,
  "label": ""
  }

  # Print these details for review in case something goes wrong.
  pp.pprint(query_details)

  return query_details


def get_data(MOES_URL, query_details):
  # POST the JSON to the url
  response = requests.post(MOES_URL, json=query_details)

  # Get the result_url
  result_url_str = response.json().get("result_url")
  print(f"RESULTS URL LOCATION:\n\n{result_url_str}\n\n")

  # Set the data_url
  data_url_str = result_url_str + "data/"

  # Get the html content of the results "data" page
  data_page = urllib.request.urlopen(data_url_str)

  # Convert it to beautiful soup content for easier handling
  soup = BeautifulSoup(data_page, "html.parser")

  # This line iterates through all hyperlinks on the 
  # results data page to find the unique "getTweets" link 
  try:
      getTweet_url_str = [link.get('href') for link in soup.findAll('a') if "getTweets" in link.text][0]
  except IndexError:
      print("~~~~~~~~\n\nNO DATA RETURNED. CHECK THE RESULT_URL TO MAKE SURE THIS IS CORRECT\n\n~~~~~~~~")
      
  # Build the url for the data page + the getTweets page
  data_tweetContent_url_str = data_url_str + getTweet_url_str

  # The next link will always be "tweetContent/" so we add that
  tweet_content = data_tweetContent_url_str + "tweetContent/"

  # We found the tweetContent page, now we need to get the specific download file urls
  # To do this, we convert the final url into beautiful soup html content
  new_html_page = urllib.request.urlopen(tweet_content)
  final_soup = BeautifulSoup(new_html_page, "html.parser")

  # Like before this line iterates through all hyperlinks on the 
  # tweetContent page to find ALL "part-m-0000*.gz" links, which 
  # automatically downloads compressed .gz files
  data_files = [link.get('href') for link in final_soup.findAll('a') if "part" in link.text]

  # Using the urllib.request.urlretrieve we mimic what wget does and download what's there.
  for file in data_files:
      urllib.request.urlretrieve(tweet_content + file,  # add the filename to this url to grab the individual file
                                 filename= f"./{file}") # save it using the same name 

  print("Finished Pulling Data.")




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUN SCRIPT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Get Moe's Tavern url with submit token...
moes_urls = get_moes_url()

## Set the type of data the user would like to return
if tweet_content:
  data_type2return = "tweet-content"
else:
  data_type2return = "tweet-id"

## Set the querytype of data the user would like to return
if user_ids:
  qtype = "userid"
else:
  qtype = "meme"

# Create the query details dictionary
query_details = create_query(qtype, data_type2return)

# Submit query details and try to download data.
try:
  get_data(moes_urls, query_details)

except:
  raise Exception("There was a problem with the download. Check the exception and the results url above to investigate.")
