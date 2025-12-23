import re

def validate_email(email):
    if not isinstance(email, str):
        return False
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def validate_price(price):
    try:
        p = float(price)
        return p >= 0
    except Exception:
        return False


def validate_name(name):
    return isinstance(name, str) and 0 < len(name) <= 40


def validate_id(idv):
    return isinstance(idv, int) and idv >= 0
