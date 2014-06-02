import json
import csv
from collections import defaultdict

USER_FILE = 'users.json'
FEEDBACK_FILE = 'personal_feedback.csv'


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
    fieldnames = ('timestamp', 'name', 'grade', 'do', '_', 'dont')
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


if __name__ == '__main__':
    users = parse_users()
    feedback = parse_feedback()
