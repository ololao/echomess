import secrets
import string


def generate_code():
    choice = string.digits
    return "".join(secrets.choice(choice) for _ in range(6))


def generate_token():
    choice = string.digits + string.ascii_letters
    return "".join(secrets.choice(choice) for _ in range(36))
