import json

USER_FILE = 'users.json'
FEEDBACK_FILE = 'personal_feedback.csv'


def parse_users():
    with open(USER_FILE) as user_file:
        user_list = json.load(user_file)

    user_dict = {}
    for user in user_list:
        email, name = user['email'], user['name']
        user_dict[name] = email

    return user_dict


def parse_feedback():
    pass


if __name__ == '__main__':
    parse_users()
