import random


def generate_card_number() -> str:
    """16-digit PAN (Visa-style prefix 4)."""
    digits = [4] + [random.randint(0, 9) for _ in range(14)]
    digits.append(random.randint(0, 9))
    return "".join(str(d) for d in digits)


def generate_cvv() -> str:
    return f"{random.randint(100, 999)}"


def format_pan(pan: str) -> str:
    digits = "".join(c for c in pan if c.isdigit())
    if len(digits) != 16:
        return pan
    return f"{digits[0:4]} {digits[4:8]} {digits[8:12]} {digits[12:16]}"


def mask_pan(pan: str, last_four: str) -> str:
    digits = "".join(c for c in pan if c.isdigit())
    if len(digits) == 16:
        return f"**** **** **** {digits[-4:]}"
    if last_four:
        return f"**** **** **** {last_four}"
    return "**** **** **** ****"
