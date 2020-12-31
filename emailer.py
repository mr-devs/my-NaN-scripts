"""
PURPOSE
    - A module for sending emails that are triggered by events occuring
    in conjunction with the twitter-streamer-V1.py script.

eMessages: A class for creating the body of the email to be sent.
    - When called, the user initializes the class with the needed
    parameters and then calls the method representative of the email
    that they want to send. Each method (daily_update, rate_limit, etc.)
    simply constructs and then returns that text message.
send_email: a method for sending the email.
    - Takes in the body of the message created by eMessage methods as
    well as the emailType, which controls the email subject as well as
    the phrase used in logging, etc.

REMEMBER TO SET MANUALLY
- myEmail
- destEmail (list)
- password (best read from environment variables with os.environ.get("VARIABLE_NAME"))

Created: 12/31/2020
Author: Matthew R. DeVerna
"""

import smtplib
from email.message import EmailMessage
import argparse
import datetime
import logging
import sys
import os

class eMessages:
    """
    Class to create the body of the email to send.
    - Methods:
        - daily_update: returns daily update email message
        - rate_limit: returns rate limiting email message
    Note: 
        - To create new email body text formats, simply 
        create a new method which returns the text you want.
        - Remember to add any new parameters to __init__() 
        so they can be utilized in the email message.
    """
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
        """Return body of daily update email text."""
        message = f"""
        || ~~~ This is an automated message from the Twitter Streamer ~~~ ||

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
        """Return body of rate limit email text."""
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
    """
    Send email message from present email address
    to preset recipient(s).
    """
    # Set email addresses and trash email password
    myEmail = "devsmoo790@gmail.com"
    destEmail = ["mdeverna@iu.edu", "mdeverna2790@gmail.com"]
    password = os.environ.get("TRASH_EMAIL_PWD")

    # Create message container 
    msg = EmailMessage()

    # Create the body of the email
    msg.set_content(email_message)

    # Create subject, and display type (for errors, etc)
    # for the message container based on emailType passed
    if emailType == 'rate_limit':
        subject = "[STREAM] - RATE LIMIT"
        displayType = "ERROR"

    elif emailType == 'daily_update':
        subject = "[STREAM] - Daily Update: Details on Stream"
        displayType = "Daily Update"

    # Update message container will all information
    msg['Subject'] = subject
    msg['From'] = myEmail
    msg['To'] = ",".join(destEmail) # Must convert to single string

    try:
        logging.info("[*] Communicating with mail server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        # Authorize the sending email address with provided password
        server.login(myEmail, password)
        server.send_message(
            msg = msg,
            from_addr = myEmail,
            to_addrs = destEmail
            )
        server.close()
        logging.info(f"[*] ~{displayType}~ email sent successfully.")
        
    # Catch all exceptions, log them, and keep going
        # We don't want to break our streamer as a result of a
        # weird email problem.
    except Exception as e:
        logging.info(f"[!] Exception Encountered: ~{displayType}~", e)
        pass
