from MoodleCrawler import config
from MoodleCrawler import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(title, message):
    user = config.mailname
    password = config.mailpass
    recipient = ', '.join(config.recipient)

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = title
    msg.attach(MIMEText(message, 'plain', 'utf-8'))
    server_ssl = smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT)
    server_ssl.ehlo()  # optional, called by login()
    server_ssl.login(user, password)
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
    server_ssl.send_message(from_addr=user, to_addrs=recipient, msg=msg.as_string())
    server_ssl.close()
    print('successfully sent the mail')
