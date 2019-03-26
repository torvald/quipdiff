import difflib
import os
import quip
from bs4 import BeautifulSoup

import config
from utils.mail import send_mail

token = config.token
state_dir = config.state_dir
threads = config.threads

output_format = config.output_format

client = quip.QuipClient(access_token=token)
user = client.get_authenticated_user()


def get_thread(thread_id):
    q = client.get_thread(thread_id)
    title = q['thread']['title']
    html = q.get("html")
    parsed_html = BeautifulSoup(html, 'html.parser')

    if output_format == "text":
        content = parsed_html.get_text()
    elif output_format == "html":
        content = parsed_html.prettify()
    elif output_format == "markdown":
        import html2markdown
        content = html2markdown.convert(html)
    else:
        raise Exception("no valid output_format in settings")

    return title, content

def get_thread_content_from_state(thread_id):
    filename = "{}/{}".format(state_dir, thread_id)
    with open(filename) as f:
        thread_content = f.read()

    return thread_content


def thread_exists(thread_id):
    filename = "{}/{}".format(state_dir, thread_id)
    return os.path.isfile(filename)


def save_thread(thread_id, thread_content):
    filename = "{}/{}".format(state_dir, thread_id)
    with open(filename, 'w') as f:
        f.write(thread_content)


def diff(old_content, new_content):
    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines()
    )
    return '\n'.join(list(diff)[3:]) # The four first lines are just +++---


def extract_thread_ids(url):
    # https://kolonialno.quip.com/O14xAEcqbOeT/Fisk-og-andre-buskevekster
    return url.split('/')[3]


for url in threads:
    # Extract thread_id and content of current version in Quip
    thread_id = extract_thread_ids(url)
    thread_title, thread_content_now = get_thread(thread_id)

    # If we have never seen the document before, save it to state and continue
    # to next document
    if not thread_exists(thread_id):
        save_thread(thread_id, thread_content_now)
        continue

    # We'll get the content of the document from last run in our state folder
    thread_content_state = get_thread_content_from_state(thread_id)

    diff_output = diff(thread_content_state, thread_content_now)

    # Print to stdout if any changes
    if diff_output:
        # Store the new content for next round
        save_thread(thread_id, thread_content_now)

        if config.output == "gmailsmtp":
            # Sending one mail per thread with diff
            username = config.smtp_username
            password = config.smtp_password
            smtp_recipient = config.smtp_recipient
            subject = "Quipdiff in {}".format(thread_title)
            body = (' ***** {} ***** \n\n {}'.format(url, diff_output))
            send_mail(username, password, smtp_recipient, subject, body)

        else:
            # stderr
            print(' ***** {} ***** '.format(thread_title))
            print(' ***** {} ***** '.format(url))
            print("\n" + diff_output + "\n")
