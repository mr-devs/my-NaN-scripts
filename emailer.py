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
import logging
import sys


def send_email(
    email_lines = list,
    subject = str,
    from_email = str,
    password = str,
    to_emails = list,
    log_name = "Not Set.",
    host = 'smtp.gmail.com',
    port = 465
    ):
    """
    Send email message based on parameters provided.

    Required Paramters:
    - email_lines (list): A list of lines for the email. Each line 
    in the list concatenated together with a next line character
        (for example, via "\\n ".join(email_lines))
    - subject (str): The subject headline of the email
    - from_email: The email address which you'd like to send the 
    email from.
    - password (str): Password for `from_email`
    - to_emails (list): Emails to send the email to.
    - log_name (str): If using send_email within another script 
    that is writing updates to a log, this will be the name referred
    to in the log file.
        - default = "Not Set."

    Optional Paramters:
    - host (str): Host to use for email sending. See smtplib for details
        - default = "smtp.gmail.com" for sending from gmail email accounts
    - port (int): Port to use for email sending

    Example Usage:
    #import packages
    import os
    from emailer import send_email

    # Use os to load email password from terminal environment
    password = os.environ.get("EMAIL_PWD")
    # Set subject line of email
    subject = "test email"
    # Create email body content. Each list object is one line
    lines = ["Like, this is your father.", "OMG, no way!" "**akward silence**", "Goodbye.","\t-Darth Vadar"]
    # Set emails
    from_ = "sendfromthisemail@gmail.com"
    send2 = ["receiver1@gmail.com","receiver2@gmail.com"]
    # Call Function
    send_email(
        email_lines = lines,
        subject = subject,
        log_name = "test email",
        from_email = from_,
        password = password,
        to_emails = send2)
    """

    # Check types
    if not isinstance(email_lines, list):
        raise TypeError("`email_lines` must be a list where each line represents one line in the body of the email email")    
    if not isinstance(subject, str):
        raise TypeError("`subject` must be a string")
    if not isinstance(log_name, str):
        raise TypeError("`log_name` must be a string")
    if not isinstance(from_email, str):
        raise TypeError("`from_email` must be a string")
    if not isinstance(password, str):
        raise TypeError("`password` must be a string")
    if not isinstance(to_emails, list):
        raise TypeError("`to_emails` must be a string")
    if not isinstance(host, str):
        raise TypeError("`host` must be a string")
    if not isinstance(port, int):
        raise TypeError("`port` must be a string")

    # Create message container 
    msg = EmailMessage()

    # Create the body of the email
    msg.set_content("\n".join(email_lines))

    # Update message container will all information
    msg['Subject'] = subject
    msg['From'] = from_email

    # This if-statement handles whether one vs. multiple
    # emails are provided.
    if len(to_emails) == 1:
        msg["To"] = str(to_emails[0])
    else:
        to_emails = [str(x) for x in to_emails] # Ensure all emails are strigns
        msg['To'] = ",".join(to_emails)         # Convert to single string

    try:
        logging.info("[*] Communicating with mail server...")
        server = smtplib.SMTP_SSL(host, port)
        server.ehlo()
        # Authorize the sending email address with provided password
        server.login(from_email, password)
        server.send_message(
            msg = msg,
            from_addr = from_email,
            to_addrs = to_emails
            )
        server.close()
        logging.info(f"[*] Email sent successfully. Email Type: ~{log_name}~")
        print("Email sent successfully.")
        
    # Catch all exceptions, log them, and keep going
        # We don't want to break something as a result of a
        # weird email problem.
    except Exception as e:
        logging.info(f"[!] Exception Encountered. Email Type: ~{log_name}~", e)
        print(f"[!] Exception Encountered. Email Type: ~{log_name}~", e)
        pass
