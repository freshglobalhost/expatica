from django.core.management.base import BaseCommand

from apps.support.models import FAQ, HelpArticle, HelpCategory


CATEGORIES = [
    ("getting-started", "Getting Started", 1),
    ("accounts-wallets", "Accounts & Wallets", 2),
    ("loans-credit", "Loans & Credit", 3),
    ("savings-investments", "Savings & Investments", 4),
    ("cards-payments", "Cards & Payments", 5),
    ("security-compliance", "Security & Compliance", 6),
]


FAQS = [
    (
        "getting-started",
        1,
        "What is PennyCredit and who is it for?",
        "PennyCredit is a digital banking platform that combines everyday money management with lending, savings, investments, virtual cards, and crypto deposits in one secure dashboard. It is designed for individuals and small businesses who want transparent fees, fast loan decisions, and modern tools without visiting a branch. After you sign up and complete identity verification, you can fund your wallet, apply for credit, open savings goals, and invest from the same account.",
    ),
    (
        "accounts-wallets",
        2,
        "How do I add money to my PennyCredit wallet?",
        "You can fund your USD wallet through bank transfer methods shown under Send & Receive, or by submitting a crypto deposit (BTC, ETH, USDT, or SOL) with the required amount and proof of payment. Crypto deposits are credited after our team verifies the transaction on-chain. Your dashboard balance updates automatically once a deposit is approved. Always double-check the wallet address and network before sending digital assets.",
    ),
    (
        "loans-credit",
        3,
        "How long does loan approval take?",
        "Most applications are reviewed within one business day after you submit all required documents (government ID, proof of income, and completed application fields). You can track status under Loans → Application history. When an administrator approves your application, a loan record and repayment schedule are created automatically and funds are disbursed to your primary wallet. You will see the active loan on your dashboard and can view each installment due date.",
    ),
    (
        "loans-credit",
        4,
        "What interest rates apply to PennyCredit loans?",
        "Rates depend on the loan product (personal, business, home, or auto), the amount requested, term length, and your profile. Each product displays a minimum APR on the marketplace before you apply. Your final rate is confirmed at approval and shown on the loan details page together with principal, outstanding balance, and the full repayment schedule. Use the in-app loan calculator to estimate monthly payments before applying.",
    ),
    (
        "savings-investments",
        5,
        "How do savings goals and locked savings work?",
        "Savings goals let you name a target, set an amount and optional target date, and track progress over time. Locked savings accounts hold funds until a fixed unlock date while earning the advertised rate for that lock period. Auto-save rules can move money on a schedule you configure (stored as rule settings in your account). All savings activity appears in your savings history with reference codes for deposits and transfers.",
    ),
    (
        "savings-investments",
        6,
        "How do PennyCredit investment plans work?",
        "Each plan lists a minimum and maximum investment, expected return (percentage or fixed dollar amount), duration, and whether your original capital is returned at maturity. When you invest, funds are deducted from your wallet balance using your transaction PIN and locked until the maturity date. Active positions show invested amount, expected return, and days remaining. Returns are credited automatically when the plan matures, according to the plan terms shown before you confirm.",
    ),
    (
        "cards-payments",
        7,
        "How do virtual cards work on PennyCredit?",
        "You can request a virtual Visa or Mastercard from the Cards section. Each card receives a unique card number, CVV, and cardholder name based on your profile. Fund the card from your wallet, set spending limits, freeze or unfreeze instantly, and withdraw unused balance back to your wallet. Full card details require your transaction PIN via the secure reveal action. A one-time issuance fee applies when the card is created.",
    ),
    (
        "cards-payments",
        8,
        "What transfer methods are supported for sending money?",
        "PennyCredit supports wire transfer, local bank transfer, PayPal, Skrill, Google Pay, Western Union, Wise, and Payoneer. Each method has its own fields and limits shown in the send-money flow. Transfers require your four-digit transaction PIN and sufficient wallet balance. Pending transfers appear in your recent activity until processed. Fees, where applicable, are displayed before you confirm.",
    ),
    (
        "security-compliance",
        9,
        "How is my account protected?",
        "We use encrypted connections (TLS), secure password storage, optional two-factor authentication, and a separate transaction PIN for sensitive actions such as transfers, card funding, and investments. KYC verification helps prevent fraud. Never share your PIN or login credentials. If you suspect unauthorized activity, freeze your virtual cards immediately and contact support through the Help Center ticket form.",
    ),
    (
        "security-compliance",
        10,
        "What documents are required for KYC and loans?",
        "For full platform access you may be asked to verify identity with a government-issued photo ID and proof of address. Loan applications additionally require income documentation and complete employment details. Upload clear, legible files in PDF or image format. Incomplete applications remain in pending status until an administrator can review them. Approved KYC unlocks higher limits and faster processing.",
    ),
]


ARTICLES = [
    (
        "getting-started",
        "create-and-verify-account",
        "How to create and verify your PennyCredit account",
        """## Overview
Creating a PennyCredit account takes only a few minutes. Verification unlocks transfers, loans, cards, and higher limits.

## Step 1: Sign up
Visit the registration page and provide your legal name, email, phone number, and a strong password. You must accept the terms of service and privacy policy. Choose a username that you will use alongside your email at login.

## Step 2: Complete your profile
From **Settings → Profile**, add your address, country, and gender if requested. Upload a profile photo if desired. Accurate information speeds up KYC and ensures cardholder names match your identity.

## Step 3: Set your transaction PIN
Before sending money, funding cards, or investing, set a **four-digit transaction PIN** under security settings. This PIN is separate from your login password and is required for high-risk actions.

## Step 4: Submit KYC documents
Upload a clear photo of your government ID and any requested proof of address. Our compliance team typically reviews submissions within 24–48 hours. You will see **KYC status** on your dashboard.

## Step 5: Fund your wallet
Use **Crypto Deposit** or supported transfer methods to add USD to your primary wallet. Your dashboard shows available balance, recent transactions, and quick links to savings, loans, and investments.

## Need help?
Open **Help → Submit ticket** or browse FAQs if verification is delayed more than two business days.""",
    ),
    (
        "accounts-wallets",
        "understanding-wallet-balances",
        "Understanding your wallet and dashboard balances",
        """## Primary USD wallet
Your main wallet holds United States dollars available for transfers, card funding, loan repayments, and investments. The dashboard **Available balance** reflects funds you can spend immediately.

## Crypto balances
Separate balances track BTC, ETH, USDT, and SOL held on the platform. Crypto deposit addresses are unique per asset—always confirm the symbol and network before sending. Deposits create a pending transaction until verified.

## Deposit vs loan balance
The dashboard may show **deposit balance** (funds you added) and **loan balance** (outstanding debt) separately so you can see net financial position at a glance.

## Transaction history
Every credit and debit includes a **reference code**, category, status, and timestamp. Filter recent activity from the dashboard or open the full transaction list for exports and support inquiries.

## Tips
- Keep a small buffer for card issuance fees and transfer fees.
- Use your transaction PIN only on the official PennyCredit site or app.
- Report unrecognized transactions immediately via a support ticket.""",
    ),
    (
        "accounts-wallets",
        "crypto-deposit-guide",
        "Crypto deposit guide (BTC, ETH, USDT, SOL)",
        """## Before you send
1. Open **Crypto Deposit** from the dashboard.
2. Select the asset (BTC, ETH, USDT, or SOL).
3. Copy the displayed wallet address—do not type it manually.
4. Send at least the **minimum deposit** amount listed for that asset.

## Submitting proof
After sending, enter the amount, transaction hash (if available), and upload proof (screenshot or receipt). Required fields must be completed or the deposit cannot be queued for review.

## Verification timeline
Deposits are credited after on-chain confirmation and manual review. You will see a pending transaction with status updates. Once approved, your crypto balance and USD valuation (where applicable) update automatically.

## Important warnings
- Sending on the wrong network may result in permanent loss of funds.
- PennyCredit will never ask you to send crypto to an address given over phone or chat.
- SOL and other assets must match the deposit page symbol exactly.""",
    ),
    (
        "loans-credit",
        "how-to-apply-for-a-loan",
        "How to apply for a loan on PennyCredit",
        """## Choose a product
Visit **Loans** to compare Personal, Business, Home, and Auto products. Each card shows minimum and maximum amounts, starting APR, and available terms.

## Prepare documents
Have digital copies of:
- Government-issued photo ID
- Proof of income (pay stub, tax return, or business statement)
- Supporting information for your employment fields

## Complete the application
The multi-step form collects amount, term, purpose, contact details, and uploads. **All fields are required.** Review the summary before submitting.

## After submission
Your application receives a unique reference code and **pending** status. You cannot edit a submitted application—contact support if you made an error.

## Approval and disbursement
When an administrator sets status to **approved**, PennyCredit automatically:
1. Creates a **Loan** record with your rate and term
2. Generates the **repayment schedule**
3. Credits your wallet with the principal amount

Track active loans under **Loans → History** and open any loan for installment details.""",
    ),
    (
        "loans-credit",
        "repaying-your-loan",
        "Repaying your loan and managing installments",
        """## Repayment schedule
Each approved loan includes monthly installments with due dates and amounts. Open **Loans → [your loan] → Repayment** to see upcoming and paid installments.

## Making payments
Pay installments from your wallet balance using the repayment flow. Ensure sufficient funds before the due date to avoid late fees (where applicable under your loan agreement).

## Outstanding balance
The loan details page shows **principal**, **interest rate**, **outstanding balance**, and status. As you pay, outstanding balance decreases until the loan is **closed**.

## Early payoff
Contact support if you wish to settle the full balance early. Administrator notes may be required depending on product type.

## Trouble paying?
Submit a ticket under **Help** before a due date passes. Support can discuss restructuring options where policy allows.""",
    ),
    (
        "savings-investments",
        "building-savings-goals",
        "Building savings goals and auto-save rules",
        """## Savings goals
Create a goal with a name, target amount, and optional target date label. Progress bars show how much you have saved versus your target. Multiple goals can run in parallel (vacation, emergency fund, home down payment).

## Depositing to a goal
Record deposits through savings transactions linked to a goal. Each entry receives a **SAV-** reference code for your records.

## Locked savings
Locked accounts earn a published rate for a fixed period. Funds cannot be withdrawn until the **unlock date**. Use locked savings for amounts you will not need immediately.

## Auto-save rules
Enable rules such as rounding up purchases or monthly transfers. Toggle rules on or off from the Savings dashboard. Saved totals accumulate in **total saved amount** per rule.

## Best practices
Set realistic targets, prioritize an emergency fund, and review progress monthly from the analytics section.""",
    ),
    (
        "savings-investments",
        "investment-plans-explained",
        "Investment plans: returns, duration, and risk",
        """## Plan types
PennyCredit offers multiple plans ranging from short **7-day** starter products to **12-month** high-yield options. Each plan specifies:
- Minimum and maximum investment
- Return type (**percent** of principal or **fixed** dollar return)
- Duration label (lock period)
- Whether **capital is returned** at maturity

## Confirming an investment
On the invest screen, enter an amount within plan limits, review expected ROI and total return, accept the lock terms, and enter your **transaction PIN**. Funds leave your wallet immediately and the position becomes **active**.

## Maturity
When the lock period ends, status moves to **matured** and returns post to your wallet per plan rules. ROI-only plans return profit without returning principal—read the plan card carefully.

## Portfolio view
**My Investments** lists active and matured positions with days remaining and progress indicators. Use it to track total invested and expected returns.

## Risk disclosure
Investments are not insured deposit products. Only invest amounts you can afford to lock for the full duration.""",
    ),
    (
        "cards-payments",
        "virtual-card-guide",
        "Virtual card guide: create, fund, freeze, withdraw",
        """## Requesting a card
Go to **Cards → Request new card**, choose network (Visa or Mastercard), theme, name, and spending limit. Pay the issuance fee from your wallet using your transaction PIN.

## Card details
Each card has a unique number, CVV, expiry, and **cardholder name** from your profile. The front of the card shows a masked number; use **View details** with PIN to reveal full data.

## Funding and withdrawing
**Fund** moves USD from your wallet to the card balance (minimum $10). **Withdraw** moves unused card balance back to your wallet. Both require your transaction PIN.

## Freeze and unfreeze
Freeze instantly blocks new spend. Unfreeze restores normal use. You cannot fund a frozen card until it is unfrozen.

## Spending limit
Set a monthly spending cap when creating or editing the card. Track **spent this month** on the card detail panel.""",
    ),
    (
        "cards-payments",
        "send-money-and-transfers",
        "Sending money with PennyCredit transfer methods",
        """## Supported rails
PennyCredit integrates eight transfer methods: Wire, Local, PayPal, Skrill, Google Pay, Western Union, Wise, and Payoneer. Availability may depend on your region and verification level.

## How to send
1. Open **Send money** from the dashboard or **View all** methods.
2. Select a method and complete recipient fields.
3. Enter amount and note; confirm fees if shown.
4. Enter your **transaction PIN**.

## Status and tracking
Transfers start in **pending** status. Recent transfers appear on the send page and in global transaction history with reference codes.

## Limits and security
Exceeding your available balance blocks the transfer. Never send money to recipients you do not trust. For large wires, ensure recipient banking details are correct—transfers may not be reversible.""",
    ),
    (
        "security-compliance",
        "security-best-practices",
        "Security best practices for your PennyCredit account",
        """## Password and PIN
Use a unique, strong password for login and a **different** four-digit PIN for transactions. Do not store PINs in email or screenshots.

## Phishing awareness
PennyCredit staff will never ask for your password, full card number, or PIN on social media. Always log in via the official website URL in your browser.

## Device hygiene
Keep your phone and computer updated. Avoid public Wi‑Fi when approving transfers. Log out on shared devices.

## Card controls
Freeze virtual cards when not in use. Review card transactions regularly. Withdraw excess card balance back to your wallet.

## Reporting incidents
If you notice unauthorized access, change your password immediately, freeze cards, and open a **high-priority support ticket** with timestamps and reference codes.""",
    ),
]


class Command(BaseCommand):
    help = "Seed help categories, 10 FAQs, and 10 detailed help articles."

    def handle(self, *args, **options):
        categories = {}
        for slug, name, order in CATEGORIES:
            cat, _ = HelpCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "display_order": order},
            )
            categories[slug] = cat
        self.stdout.write(self.style.SUCCESS(f"Help categories: {len(categories)}"))

        for cat_slug, order, question, answer in FAQS:
            FAQ.objects.update_or_create(
                question=question,
                defaults={
                    "answer": answer,
                    "category": categories[cat_slug],
                    "display_order": order,
                    "is_published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"FAQs: {len(FAQS)}"))

        for cat_slug, slug, title, body in ARTICLES:
            HelpArticle.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": categories[cat_slug],
                    "title": title,
                    "body": body,
                    "is_published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Help articles: {len(ARTICLES)}"))
