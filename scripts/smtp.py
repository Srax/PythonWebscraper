import pandas as pd
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from secrets import keys
import pandas as pd
import os




sender_email = keys.smtp_mail
password = keys.smtp_password
mailing_list = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'MAILING_LIST.csv')))


def send_mail_to_all_on_mailing_list(subject, data):
    print(">>>>> Sending out stock update emails")
    for x, email in enumerate(mailing_list.email):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email


        # Create the plain-text and HTML version of your message
        text = """\
            Item in stock!
            {itemList}
            
        """
        html = """\
        <html>
        <body>
        <h2>Item back in stock!</h2>
        {dat}
        </body>
        </html>
        """
        html = html.format(dat = data.to_html())

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, email, message.as_string()
            )

def send_main_plain(subject, msg):
    for x, email in enumerate(mailing_list.email):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email


        # Create the plain-text and HTML version of your message
        text = """\
            {msg}            
        """
        html = """\
        <html>
        <body>
        {txt}
        </body>
        </html>
        """
        html = html.format(txt = msg)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, email, message.as_string()
            )