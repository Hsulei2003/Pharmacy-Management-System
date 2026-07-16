# authentication/session.py

current_user = None


def login(user: dict):
    global current_user
    current_user = user


def logout():
    global current_user
    current_user = None


def is_logged_in():
    return current_user is not None


def get_current_user():
    return current_user