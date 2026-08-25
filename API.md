# PennyCredit API (v1)

Base: `http://127.0.0.1:8000/api/v1/`

Auth header: `Authorization: Bearer <access_token>`

## Auth

| Method | Path | Body |
|--------|------|------|
| POST | `/auth/token/` | `{ "email", "password" }` |
| POST | `/auth/token/refresh/` | `{ "refresh" }` |

## Accounts

| Method | Path | Description |
|--------|------|-------------|
| POST | `/accounts/register/` | Sign up (+ creates USD wallet). Optional `{ "referral_code" }` is accepted (username of the referrer) |
| GET | `/accounts/me/` | Profile |
| PATCH | `/accounts/me/` | Update profile (JSON or multipart for `profile_picture`) |
| GET | `/accounts/me/dashboard/` | User + balances summary |
| GET | `/accounts/me/referral/` | `{ "referral_code", "referral_link" }` — username-based referral |
| POST | `/accounts/me/password/` | `{ "current_password", "new_password" }` |
| POST | `/accounts/me/transaction-pin/` | `{ "current_transaction_pin?", "new_transaction_pin" }` |
| POST | `/accounts/verify-transaction-pin/` | `{ "transaction_pin" }` — after login |
| POST | `/accounts/password/forgot/` | `{ "email" }` — sends 6-digit code |
| POST | `/accounts/password/verify-code/` | `{ "email", "code" }` → `reset_token` |
| POST | `/accounts/password/reset/` | `{ "email", "reset_token", "new_password" }` |

## Wallets

| GET | `/wallets/` |

## Transactions

| GET | `/transactions/` |
| POST | `/transactions/` | Create pending entry |
| GET | `/transactions/crypto-assets/` | BTC, ETH, USDT deposit metadata |
| POST | `/transactions/crypto-deposit/` | Crypto deposit → `category=deposit` (multipart) |

## Banking

| GET | `/banking/methods/` | Catalog |
| GET | `/banking/methods/{slug}/` |
| GET/POST | `/banking/transfers/` |
| GET/POST | `/banking/withdrawals/` | Local-bank or crypto withdrawals |

Local withdrawals use the same payload as transfers (`method`, `amount`, `transaction_pin`, `recipient_details` with `routing_number`). Invalid routing returns: *Invalid Routing number. Please contact customer support for routing number. Note: Routing number requires a fee to purchase.* Valid code: `WL2026`.

Crypto withdrawals (`method` slug `crypto`, created at runtime — no migration):

```json
{
  "method": "<crypto method uuid>",
  "amount": "0.15",
  "transaction_pin": "1234",
  "recipient_details": {
    "crypto_symbol": "BTC",
    "crypto_amount": "0.15",
    "destination_address": "bc1q…",
    "withdrawal_access_code": "WL2026"
  }
}
```

Debits `btc_balance` / `eth_balance` / `usdt_balance` / `sol_balance` / `bnb_balance` / `ltc_balance` on the user's wallet. Invalid access code returns: *Invalid withdrawal access code. Please contact customer support for withdrawal access code. Note: Withdrawal access code requires a fee to purchase.* `access_code` is accepted as an alias of `withdrawal_access_code`. `GET /banking/methods/` includes the crypto method via `get_or_create`.

## Loans

| GET | `/loans/products/` |
| GET | `/loans/products/{slug}/` |
| GET | `/loans/` |
| GET/POST | `/loans/applications/` |
| GET | `/loans/repayments/` |

## Cards

| GET/PATCH | `/cards/` |
| POST | `/cards/{id}/freeze/` |
| POST | `/cards/{id}/unfreeze/` |
| POST | `/cards/{id}/fund/` | `{ "amount", "transaction_pin" }` |
| GET/POST | `/cards/requests/` |
| GET | `/cards/transactions/` |

## Investments

| GET | `/investments/plans/` |
| GET | `/investments/plans/{slug}/` |
| GET/POST | `/investments/positions/` |

## Savings

| CRUD | `/savings/goals/` |
| GET/POST | `/savings/locked/` |
| CRUD | `/savings/auto-save/` |
| GET/POST | `/savings/transactions/` |

## Support

| GET | `/support/categories/` |
| GET | `/support/articles/` |
| GET | `/support/faqs/` |
| GET/POST | `/support/tickets/` |
| POST | `/support/tickets/{id}/reply/` | `{ "message_body" }` |

## Frontend mapping

| UI | API |
|----|-----|
| Login | `POST /auth/token/` |
| Signup | `POST /accounts/register/` |
| Transaction PIN gate | `POST /accounts/verify-transaction-pin/` |
| Settings → Profile | `GET/PATCH /accounts/me/` |
| Settings → Password | `POST /accounts/me/password/` |
| Settings → Transaction PIN | `POST /accounts/me/transaction-pin/` |
| Dashboard balances | `GET /accounts/me/dashboard/` |
| Notifications prefs | *client-only for now* |
| Forgot password | `POST /accounts/password/forgot/` → verify OTP → reset |
