import requests
from bs4 import BeautifulSoup
import urllib.request
import sys

# Comes from the Tavern interface. Copy & paste.
url = 'https://carl.cs.indiana.edu/moe/api/submit_query?token=89b98ddc-3d81-4780-ad5b-0076e31d68ef'
payload = payload = {
  "email": "mdeverna@iu.edu",
  "qtype": "meme",
  "q": "#blessed",
  "start": "2020-12-01T00:00",
  "end": "2020-12-10T00:00",
  "output": "tweet-content",
  "label": ""
}

# POST the JSON to the url
response = requests.post(url, json=payload)

# Get the result_url
result_url_str = response.json().get("result_url")

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
    print("No data returned. Check the result_url page to make sure this is correct.")
    sys. exit(result_url_str)
    
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