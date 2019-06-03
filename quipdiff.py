import difflib
import os
import quip
import time
from bs4 import BeautifulSoup

import config
from utils.mail import send_mail, html_enclose, html_colorize_diff

token = config.token
state_dir = config.state_dir
diff_starred = config.diff_starred
threads = config.threads
folder_ids = config.folder_ids
thread_ids = config.thread_ids

output_format = config.output_format

client = quip.QuipClient(access_token=token)
user = client.get_authenticated_user()


def get_thread(thread_id):
    q = client.get_thread(thread_id)
    link = q["thread"]["link"]
    title = q["thread"]["title"]
    html = q.get("html")
    parsed_html = BeautifulSoup(html, "html.parser")

    if output_format == "text":
        content = parsed_html.get_text()
    elif output_format == "html":
        content = parsed_html.prettify()
    elif output_format == "markdown":
        import html2markdown

        content = html2markdown.convert(html)
    else:
        raise Exception("no valid output_format in settings")

    return title, content, link


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
    with open(filename, "w") as f:
        f.write(thread_content)


def diff(old_content, new_content):
    diff = difflib.unified_diff(old_content.splitlines(), new_content.splitlines())
    return "\n".join(list(diff)[3:])  # The four first lines are just +++---


def extract_thread_ids(url):
    # https://kolonialno.quip.com/O14xAEcqbOeT/Fisk-og-andre-buskevekster
    return url.split("/")[3]

# TODO: clean this up, make a main() and dry up a bit
if diff_starred:
    starred = client.get_folder(user["starred_folder_id"])
    for star in starred["children"]:
        if "folder_id" in star:
            folder_ids.append(star["folder_id"])
        if "thread_id" in star:
            thread_ids.append(star["thread_id"])

for folder_id in folder_ids:
    folder = client.get_folder(folder_id)
    for item in folder["children"]:
        if "thread_id" in item:
            thread_ids.append(item["thread_id"])

for url in threads:
    # Extract thread_id and content of current version in Quip
    thread_ids.append(extract_thread_ids(url))

rate_limit_trottle_time = 0

if len(thread_ids) > 50:
    # Since quip rate limits 50 request per minute, we need to ensure we dont
    # exceed that by adding two seconds between every request
    rate_limit_trottle_time = 2

if len(thread_ids) > 900:
    # If you run this script at every hour (which is what I would recommend),
    # you can not request more the 900 documents, as this is the rate limit per
    # hour. You should propably not reach this limit anyway.
    raise Exception("Nope, got to many docs to parse ({})".format(len(thread_ids)))

for thread_id in thread_ids:
    time.sleep(rate_limit_trottle_time)
    thread_title, thread_content_now, thread_link = get_thread(thread_id)

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
            body_plain = " ***** {} ***** \n\n {}".format(thread_link, diff_output)
            body_html = html_enclose(html_colorize_diff(body_plain))
            send_mail(
                username, password, smtp_recipient, subject, body_plain, body_html
            )

        else:
            # stderr
            print(" ***** {} ***** ".format(thread_title))
            print(" ***** {} ***** ".format(thread_link))
            print("\n" + diff_output + "\n")
