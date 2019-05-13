# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(user, pwd, recipient, subject, body):

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    plaintext = MIMEText(TEXT, "plain", "utf-8")
    msg.attach(plaintext)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
    except Exception as e:
        import traceback

        print(traceback.format_exc())
