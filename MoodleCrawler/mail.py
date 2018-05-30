from MoodleCrawler import config
from MoodleCrawler import settings
import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from email.message import EmailMessage

changed_courses = {}

user = config.mailname
password = config.mailpass


def send_mail(title, recipient, course_key, message=None):
    if message:
        # _send_mail(title, message, recipient)
        print_mail(title, message, recipient)
        changed_courses[course_key] = message
    else:
        if course_key in changed_courses:
            # _send_mail(title, changed_courses[course_key], recipient)
            print_mail(title, changed_courses[course_key], recipient)


def _send_mail(title, message, recipient):
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


def print_mail(title, message, recipient):
    print('title:', title)
    print('message', message)
    print('recipient', recipient)


if __name__ == '__main__':
    _send_mail('test', 'test', '151250093@smail.nju.edu.cn')
