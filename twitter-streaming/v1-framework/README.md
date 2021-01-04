# How to use this twitter streaming framework...

> Note that **_the paths within this code will need to be updated based on your own project's folder structure_**.

### Files/Folders:
* `twitter-streamer-V1.py` : The central python script which uses `Tweepy` to filter tweets from Twitter in real-time based off of a file of tweets (see the script comments for details on how to use). Note: This script currently only captures English language tweets. To remove this restriction, remove `languages=["en"]` from line 196.
* `persistent_bash_streamer.sh` : This is a simple `bash` script which creates an infinite loop that continually restarts `twitter-streamer-V1.py` if it breaks or finishes when it is not supposed to. This is the first safety net for ensuring that the streaming script remains active continuously. Each time it restarts the script it will send you an email letting you know it has done so.
* `/cron_stuff/` (optional) : There is always the possibility that the `persistent_bash_streamer.sh` script breaks for some other reason. In order to provide a safety net for this situation, we can call `crontab -e` to edit our `cron` jobs and then add the below line. 
```bash
* * * * * bash /full/path/2/checkprocess.sh twitter-streamer-V1.py
```
  * `checkprocess.sh` : This `bash` script checks to see if a process is running (in the above case, if `twitter-streamer-V1.py` is running). 
    * Given the above line, if it is running, it would write "_twitter-streamer-V1.py Running_" in the text file, `status.txt`. 
    * If it is not running, it does the following:
      1. Changes directory to where ever you are saving data currently
      2. Automatically restarts the `persistent_bash_streamer.sh` script, which will then activates the `twitter-streamer-V1.py` under an infinite loop - effectively restarting your stream. 
          * As long as you set the `cd` line in `checkprocess.sh`correctly (i.e., to your `data` folder), this will continue to save tweets in the same file as before and the `persistent_bash_stream.sh` will append it's log to the same file. However, a new log file for the `twitter-streamer-V1.py` script will be created (though I believe this is desirable).
      3. Sends an email to whatever email you provide in the `checkprocess.sh` script.
      	  * Subject of that email will be --> "Cron/Stream Update" (or whatever you change it to be)
      	  * Body of that email is the contents of `email_notification.txt` - feel free to update this file as you see fit.


### Steps to start gathering tweets with this streaming pipeline:
1. Edit `persistent_bash_streamer.sh` to include your own Twitter API tokens/keys as well as the proper path to your `twitter-streamer-V1.py` script and filter keywords file.
2. Create a `data/` folder which will store your streamed tweets and log files.
3. Edit the paths within the checkprocess.sh file to match your own project directory.
4. Change directories to the `data/` folder and run `bash persistent_bash_streamer.sh`. This will begin streaming tweets which include the terms in the keywords file that you are providing `twitter-streamer-V1.py`
5. (Optional) Add the above line to your cron jobs by calling `crontabs -e` and pasting the above line into that file. 



