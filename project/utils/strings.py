from django.utils.crypto import get_random_string
import re, random, math, os, base64
import string, uuid
import secrets

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def dash_sep(string, n=4):
    """
    adds a `-` to the `string` parameter for every
    character count denoted by `n`
    """
    new_str = ""
    for index, s in enumerate(string):
        if index % n == 0 and index != 0:
            new_str += "-"
        new_str += s

    return new_str


def generate_ref_no(amount=6):
    """generates random characters `amount` number of times"""
    return f"{get_random_string(amount)}".upper()


def generate_random_colour():
    """generate random colours"""
    hexnum = get_random_string(6, "0123456789abcdef").lower()
    return f"#{hexnum}"


def generate_invite_code(amount=16):
    return get_random_string(amount)


def get_words_from_html(raw_html):
    clean_text = re.sub(CLEANR, '', raw_html)
    word_list = re.findall(r'\w+', clean_text.strip())
    return word_list


def generate_ref_code():
    code =str(uuid.uuid4()).replace("-", "")[:12]
    return code


def generate_coupon_code():
    token = os.urandom(15)
    code = re.sub(r'[^\w]', '', str(base64.b64encode(token)))
    return code


def generate_checker_pin():
    alphabet = string.digits
    pin_length = 10
    code = ''.join(secrets.choice(alphabet) for _ in range(pin_length))
    return code


def get_otp(amount=6):
    digits = "0123456789"
    OTP = ""
    for i in range(amount) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def generate_serial():
    return ''.join(random.choice('0123456789') for _ in range(20))