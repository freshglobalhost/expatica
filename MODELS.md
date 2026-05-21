# PennyCredit data model map

Models mirror frontend mock data in `lib/*-mock-data.ts` and `lib/transfer-methods.ts`.

## accounts

| Model | Fields |
|-------|--------|
| `User` | `email`, `phone`, `country`, `address`, `gender`, `profile_picture`, `transaction_pin`, `kyc_status` |

## wallets

| Model | Fields |
|-------|--------|
| `Wallet` | `currency_code` (ISO fiat choices, default USD), `balance`, `btc_balance`, `eth_balance`, `usdt_balance` |

## transactions

| Model | Fields |
|-------|--------|
| `Transaction` | `direction`, `category`, `amount`, `currency_code`, `status`, `reference_code`, `description`, `counterparty_name`, `crypto_symbol`, `crypto_amount`, `transaction_hash`, `proof_image` |

## banking

| Model | Fields |
|-------|--------|
| `TransferMethod` | `slug`, `name`, `category`, `display_order` |
| `Transfer` | `amount`, `fee_amount`, `recipient_details`, `reference_code`, `status` |

## loans

| Model | Fields |
|-------|--------|
| `LoanProduct` | `slug`, `minimum_amount`, `maximum_amount`, `minimum_interest_rate`, `available_terms_months` |
| `LoanApplication` | `requested_amount`, `term_months`, `reference_code` |
| `Loan` | `principal_amount`, `outstanding_balance`, `applied_on`, `disbursed_on` |
| `LoanRepayment` | `amount`, `due_on`, `paid_on` |

## cards

| Model | Fields |
|-------|--------|
| `VirtualCard` | `card_name`, `last_four_digits`, `monthly_spent_amount`, `is_frozen` |
| `CardRequest` | `card_name`, `issuance_fee` |
| `CardTransaction` | `merchant_name`, `amount` |

## investments

| Model | Fields |
|-------|--------|
| `InvestmentPlan` | `slug`, `return_type`, `return_value`, `duration_label` |
| `UserInvestment` | `invested_amount`, `expected_return_amount`, `matures_at` |

## savings

| Model | Fields |
|-------|--------|
| `SavingsGoal` | `goal_name`, `target_amount`, `saved_amount` |
| `LockedSavingsAccount` | `account_name`, `locked_amount`, `unlocks_on` |
| `AutoSaveRule` | `rule_name`, `rule_settings`, `is_enabled` |
| `SavingsTransaction` | `reference_code`, `transaction_type`, `amount` |

## support

| Model | Fields |
|-------|--------|
| `HelpCategory`, `HelpArticle`, `FAQ` | Help center content |
| `SupportTicket`, `TicketMessage` | `reference_code`, `message_body` |
