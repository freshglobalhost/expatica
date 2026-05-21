import uuid


def generate_reference_code(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"
