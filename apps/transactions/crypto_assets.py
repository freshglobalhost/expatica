"""Supported crypto assets for deposits (configured in-app, no separate crypto app)."""

from decimal import Decimal

CRYPTO_ASSETS = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "network_name": "Bitcoin Network",
        "deposit_wallet_address": "3GFTjjZTPGKRMpE16N53fJKgwjWnNrNKBS",
        "minimum_deposit_amount": Decimal("0.0001"),
        "required_confirmations": 3,
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "network_name": "Ethereum (ERC-20)",
        "deposit_wallet_address": "0xF355071A0e54211763218E0C99E463094B772a87",
        "minimum_deposit_amount": Decimal("0.01"),
        "required_confirmations": 12,
    },
    {
        "symbol": "USDT",
        "name": "Tether",
        "network_name": "Tron (TRC-20)",
        "deposit_wallet_address": "TT3jJibKkRKRDJa5TkYHeUwKEagofRdkzY",
        "minimum_deposit_amount": Decimal("10"),
        "required_confirmations": 12,
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "network_name": "Solana Network",
        "deposit_wallet_address": "45GC1UypduTvTgyue5CUAhVKbc5YCiKEHB1p9uEQBAr2",
        "minimum_deposit_amount": Decimal("0.1"),
        "required_confirmations": 32,
    },
]

CRYPTO_SYMBOLS = {asset["symbol"] for asset in CRYPTO_ASSETS}
