# PennyCredit API (Django REST Framework)

Backend for the PennyCredit Next.js frontend. Organized into domain apps under `apps/`.

## Apps

| App | Purpose |
|-----|---------|
| `accounts` | Users, transaction PIN |
| `wallets` | Multi-currency balances |
| `transactions` | Ledger / activity feed |
| `banking` | Send money (wire, PayPal, etc.) |
| `loans` | Products, applications, repayments |
| `cards` | Virtual cards, requests, card txns |
| `investments` | Plans and user investments |
| `savings` | Goals, locked savings, auto-save |
| `support` | Help articles, FAQ, tickets |

See [MODELS.md](./MODELS.md) for field-level mapping to the frontend.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

`seed_catalog` creates loan products (`personal`, `business`, `home`, `auto`) and transfer methods (`wire`, `paypal`, etc.) required by the dashboard.

API base: `http://127.0.0.1:8000/api/v1/`

- Health: `GET /api/v1/health/`
- JWT: `POST /api/v1/auth/token/` (email + password once serializers are added)

## Settings

Edit values directly in:

- `project/development_settings.py` — local dev (default for `manage.py`)
- `project/production_settings.py` — production hosts, DB URL, secret key
- `project/base_settings.py` — shared config (CORS origins, apps, etc.)
