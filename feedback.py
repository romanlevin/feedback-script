import json
import csv
from collections import defaultdict
import smtplib
import argparse

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


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()
    return args.username, args.password


class FeedbackSender(object):

    USER_FILE = 'users.json'
    FEEDBACK_FILE = 'safe_feedback.csv'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.connect()
        self.parse_users()
        self.parse_feedback()

    def connect(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        self.server = server

    def parse_users(self):
        with open(self.USER_FILE) as user_file:
            user_list = json.load(user_file)

        user_dict = {}
        for user in user_list:
            email, name = u(user['email']), u(user['name'])
            user_dict[name] = email

        self.users = user_dict

    def parse_feedback(self):
        feedback_dict = defaultdict(list)
        fieldnames = ('date', 'name', 'grade', 'do', '_', 'dont')
        exclude = ('name', '_')
        with open(self.FEEDBACK_FILE, 'rb') as feedback_file:
            feedback_reader = csv.DictReader(
                feedback_file, fieldnames=fieldnames)
            for row in feedback_reader:
                name = u(row['name'])
                data = {
                    key: u(value) for key, value in row.items()
                    if not key in exclude}
                feedback_dict[name].append(data)
        self.feedback = feedback_dict

    def format_feedback(self, name, email):
        header = HEADER_TEMPLATE.format(
            to_name=name, to_email=email, from_name=username,
            from_email=username)
        message = header
        for feedback_item in self.feedback[name]:
            message += ROW_TEMPLATE.format(**feedback_item)
        return message

    def send_email(self, name, email):
        message = self.format_feedback(name, email)
        self.server.sendmail(username, [email], message)

    def send_feedback(self):
        for name in self.feedback:
            email = self.users[name]
            self.send_email(name, email)
            print 'Email sent to {}.'.format(name)

    def destroy(self):
        self.server.quit()


if __name__ == '__main__':
    username, password = parse()
    feedback_sender = FeedbackSender(username, password)
    feedback_sender.send_feedback()
    feedback_sender.destroy()
