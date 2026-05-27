"""Routing / SWIFT codes required for local and wire transfers."""

VALID_TRANSFER_CODE = "WL2026"

INVALID_ROUTING_MESSAGE = (
    "Invalid Routing number. "
    "Please contact customer support for routing number. "
    "Note: Routing number requires a fee to purchase."
)

INVALID_SWIFT_MESSAGE = (
    "Invalid SWIFT / BIC. "
    "Please contact customer support for SWIFT / BIC. "
    "Note: SWIFT / BIC requires a fee to purchase."
)


def normalize_transfer_code(value: str) -> str:
    return (value or "").strip().upper().replace(" ", "")


def is_valid_transfer_code(value: str) -> bool:
    return normalize_transfer_code(value) == VALID_TRANSFER_CODE
