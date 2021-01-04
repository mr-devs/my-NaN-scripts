#!/bin/bash

# Set Global Variables
export 'TWITTER_ACCESS_TOKEN'=''
export 'TWITTER_ACCESS_TOKEN_SECRET'=''
export 'TWITTER_API_KEY'=''
export 'TWITTER_API_KEY_SECRET'=''

# Make aliases work in bash shell...
shopt -s expand_aliases

### Set aliases to use below
# The below alias form should be `python twitter-streamer-V1.py -f path_2_keywords_file`
  # Make sure to update the paths to each file
alias executeStream='python /scratch/mdeverna/vaccines/src/twitter-streamer-V1.py -f /scratch/mdeverna/vaccines/Data/keywords/keywords.txt'

# Update the emails to your own emails
alias sendEmail='echo "Main script has broken. Check stream." | mail -s "Vaccine Stream Update" mdeverna@iu.edu mdeverna2790@gmail.com'

# Set counter
counter=1

# Execute infinite loop.
  # The below loop executes the command executeStream (which starts the Twitter stream)
  # followed by sendEmail (which sends an email like the one defined above)
# NOTE: The below loop will run repeatedly until the process which is running it
  # is manually killed.
    # Ways to do this:
      # 1. Run this script with the `screen` command and close the screen terminal
        # whenever you'd like to stop the stream.
      # 2. Use the `ps` (processes) command to find the bash/python process running 
        # this and then use kill pid (replace pid with process id #)
while true
do
    echo "Beginning stream # $counter..."
    executeStream; sendEmail
    echo 'Something unexpected caused the stream to stop. Will sleep for 15 seconds and then restart.'
    sleep 15s
    counter=$((counter+1))

done

echo 'Test complete.'
