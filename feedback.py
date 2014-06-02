import json
import csv
from collections import defaultdict
import smtplib
import argparse

USERNAME, PASSWORD = '', ''

USER_FILE = 'users.json'
FEEDBACK_FILE = 'safe_feedback.csv'

HEADER_TEMPLATE = u"""From: {from_name} <{from_email}>
To: {to_name} <{to_email}>
Subject: Feedback

This is your feedback:

"""

ROW_TEMPLATE = u"""
*****
Date: {date}

Grade: {grade}

Do: {do}

Don't: {dont}
"""


def u(s):
    try:
        result = unicode(s, 'utf-8')
    except TypeError:
        result = s
    finally:
        return result


def parse_users():
    with open(USER_FILE) as user_file:
        user_list = json.load(user_file)

    user_dict = {}
    for user in user_list:
        email, name = u(user['email']), u(user['name'])
        user_dict[name] = email

    return user_dict


def parse_feedback():
    feedback_dict = defaultdict(list)
    fieldnames = ('date', 'name', 'grade', 'do', '_', 'dont')
    exclude = ('name', '_')
    with open(FEEDBACK_FILE, 'rb') as feedback_file:
        feedback_reader = csv.DictReader(
            feedback_file, fieldnames=fieldnames)
        for row in feedback_reader:
            name = u(row['name'])
            data = {
                key: u(value) for key, value in row.items()
                if not key in exclude}
            feedback_dict[name].append(data)
    return feedback_dict


def format_feedback(name, email, feedback, username):
    header = HEADER_TEMPLATE.format(
        to_name=name, to_email=email, from_name=username,
        from_email=username)
    message = header
    for feedback_item in feedback[name]:
        message += ROW_TEMPLATE.format(**feedback_item)
    return message


def connect(username, password):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    return server


def send_email(name, email, feedback, server, username):
    message = format_feedback(name, email, feedback, username)
    server.sendmail(username, [email], message)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()
    return args.username, args.password


if __name__ == '__main__':
    username, password = parse()
    server = connect(username, password)
    users = parse_users()
    feedback = parse_feedback()
    for name in feedback:
        email = users[name]
        send_email(name, email, feedback, server, username)
    server.quit()
