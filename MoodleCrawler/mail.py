from MoodleCrawler import config
from MoodleCrawler import settings
import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from email.message import EmailMessage


def send_mail(title, message):
    user = config.mailname
    password = config.mailpass
    recipient = config.recipient

    # msg = MIMEMultipart()
    msg = EmailMessage()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = title

    msg.set_content(message)
    # msg.attach(MIMEText(message, 'plain', 'utf-8'))
    server_ssl = smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT)
    server_ssl.ehlo()  # optional, called by login()
    server_ssl.login(user, password)
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
    server_ssl.send_message(from_addr=user, to_addrs=recipient, msg=msg)
    server_ssl.close()
    print('successfully sent the mail')


if __name__ == '__main__':
    send_mail('test', 'test')
