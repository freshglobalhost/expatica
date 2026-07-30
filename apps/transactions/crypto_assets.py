"""Supported crypto assets for deposits (configured in-app, no separate crypto app)."""

from decimal import Decimal

CRYPTO_ASSETS = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "network_name": "Bitcoin Network",
        "deposit_wallet_address": "17mfUC33P5HXAXb9Lt3cs1hcpTQ1CRV8Q6",
        "minimum_deposit_amount": Decimal("0.0001"),
        "required_confirmations": 3,
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "network_name": "Ethereum (ERC-20)",
        "deposit_wallet_address": "0x32e110a1ba1543d31f96e4819819cae8b1c9718f",
        "minimum_deposit_amount": Decimal("0.01"),
        "required_confirmations": 12,
    },
    {
        "symbol": "USDT",
        "name": "Tether",
        "network_name": "Tron (TRC-20)",
        "deposit_wallet_address": "TEBxRBr29oL3DfMaeEq5Fh86XMxWdsYAkv",
        "minimum_deposit_amount": Decimal("10"),
        "required_confirmations": 12,
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "network_name": "Solana Network",
        "deposit_wallet_address": "85UnBeGjFYpob63QBgrqc4C9y929vyABhMih2jmYuALE",
        "minimum_deposit_amount": Decimal("0.1"),
        "required_confirmations": 32,
    },
    {
        "symbol": "BNB",
        "name": "BNB",
        "network_name": "BNB Smart Chain (BEP-20)",
        "deposit_wallet_address": "0x32e110a1ba1543d31f96e4819819cae8b1c9718f",
        "minimum_deposit_amount": Decimal("0.01"),
        "required_confirmations": 15,
    },
    {
        "symbol": "LTC",
        "name": "Litecoin",
        "network_name": "Litecoin Network",
        "deposit_wallet_address": "LegGtXmTNN6XNXKjNmMAHtXRdQyUgpJn2k",
        "minimum_deposit_amount": Decimal("0.01"),
        "required_confirmations": 6,
    },
]

CRYPTO_SYMBOLS = {asset["symbol"] for asset in CRYPTO_ASSETS}
