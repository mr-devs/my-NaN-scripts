#!/bin/bash

# Use grep to try and identify if the process is running
ps_out=`ps -ef | grep $1 | grep -v 'grep' | grep -v $0`

# Record the boolean output into the variable ~result~
result=$(echo $ps_out | grep "$1")

# If true, change dir to cron_stuff and record status as Running
if [[ "$result" != "" ]];then
    cd /scratch/mdeverna/vaccines/cron_stuff
    echo "$1 Running" > status.txt

# If false, this means the stream is down.
  # As a result, we change the dir to the Data folder
  # and restart the stream with persistent_bash_streamer.sh
  # which should infinitely restart the twitter-streamer-V1.py script.
  # This is done with nohup ADDING output to the already 
  # existing nohup.out file.
  # Then we send an email to myself using email written in the
  # cron_stuff folder in the txt file email_notifcation.txt
else
    echo "$1 Not Running" > status.txt
    cd /scratch/mdeverna/vaccines/Data
    nohup python /scratch/mdeverna/vaccines/src/persistent_bash_streamer.sh >> nohup.out
    mail -s "Cron/Stream Update" mdeverna@iu.edu < /scratch/mdeverna/vaccines/cron_stuff/email_notification.txt
fi


