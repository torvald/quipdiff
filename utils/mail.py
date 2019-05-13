# Import smtplib for the actual sending function
import smtplib
import re

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def html_enclose(body):
    return """\
<html>
  <head></head>
  <body>
    {}
  </body>
</html>
""".format(
        body
    )


def html_colorize_diff(body):
    output = ""
    for line in body.splitlines():
        output += "<br>"
        if re.match("^\s*\+[^\+]", line):
            output += '<span style="color: darkgreen;">{}</span>'.format(line)
            continue
        elif re.match("^\s*\-[^\-]", line):
            output += '<span style="color: darkred;">{}</span>'.format(line)
            continue
        if re.match("^@@(.*)@@$", line):
            output += '<span style="color: darkcyan;">{}</span>'.format(line)
            continue
        output += line

    return output


def send_mail(user, pwd, recipient, subject, body_plain, body_html=None):

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body_plain

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    plaintext = MIMEText(TEXT, "plain", "utf-8")
    msg.attach(plaintext)

    if body_html:
        html = MIMEText(body_html, "html", "utf-8")
        msg.attach(html)

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
