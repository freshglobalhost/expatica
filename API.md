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
| POST | `/accounts/register/` | Sign up (+ creates USD wallet). Optional `{ "referral_code" }` uses the referrer's username |
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
| GET/POST | `/banking/withdrawals/` | Local-bank withdrawals (same payload as transfers) |

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
