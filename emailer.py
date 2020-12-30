import smtplib
from email.mime.text import MIMEText
import argparse
import datetime
import logging
import sys
import os

class eMessages:
    def __init__(
        self,
        time = "",
        log_filename = "",
        total_tweets = 0,
        todays_tweets = 0,
        rate_limits = 0
    ) -> None:
        self._time = time
        self._log_filename = log_filename
        self._total_tweets = total_tweets
        self._todays_tweets = todays_tweets
        self._rate_limits = rate_limits

    def daily_update(self):
        message = f"""
        ********************************************************************
        || ~~~ This is an automated message from the Twitter Streamer ~~~ ||
        ********************************************************************

                STREAM IS RUNNING - THIS IS AN UPDATE.

                DETAILS:
                System Report Time: {self._time}
                Total Tweets Processed: {self._total_tweets}
                Total Tweets Today: {self._todays_tweets}
                Log Filename: {self._log_filename}
                ************************************************************

        Thanks!
        - StreamerBot"""
        return message

    def rate_limit(self):
        message = f"""
        || ~~~ This is an automated message from the Twitter Streamer ~~~ ||

                THE STREAM IS BEING RATE LIMITED AND WILL WAIT 5 MINUTES.

                DETAILS:
                System Report Time: {self._time}
                Log Filename: {self._log_filename}
                Number of Times Rate Limited: {self._rate_limits}
                ******************************

        Thanks!
        - StreamerBot"""
        return message


def send_email(email_message, emailType):
    myEmail = "devsmoo790@gmail.com"
    destEmail = "mdeverna@iu.edu"
    password = os.environ.get("TRASH_EMAIL_PWD")

    # Create message container - the correct MIME type is multipart/alternative.
    message = MIMEText(email_message)

    if emailType == 'rate_limit':
        subject = "[STREAM] - RATE LIMIT"
        displayType = "ERROR"

    elif emailType == 'daily_update':
        subject = "[STREAM] - Daily Update: Details on Stream"
        displayType = "Daily Update"

    message['Subject'] = subject
    message['From'] = myEmail
    message['To'] = destEmail

    try:
        logging.info("[*] Communicating with mail server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(myEmail, password)
        server.sendmail(myEmail, destEmail, message.as_string())
        server.close()
        logging.info(f"[*] ~{displayType}~ email sent successfully.")
        

    except Exception as e:
        logging.info("[!] Exception Encountered: ", e)
        exit()