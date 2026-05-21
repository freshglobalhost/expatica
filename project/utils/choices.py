from django.db import models

Gender = models.TextChoices("Gender", ["male", "female"])
Status = models.TextChoices("Status", ["approved","paid", "pending","failed", "processing", "refunded", "rejected"])
PaymentType = models.TextChoices("Type", ['bank','virtual', 'coupon', 'paystack'])

NotificationType = models.TextChoices("Type", ['reminder', 'promotion'])

BlogStatus = models.TextChoices("BlogStatus", ["pending","reviewing","approved","rejected"])


class TransactionChoice(models.TextChoices):
    reward = 'reward'
    transfer = 'transfer'
    withdrawal = 'withdrawal'
    commission = 'commission'
    incentive = 'incentive'
    payment = 'payment'
    login_bonus = 'login_bonus'
    referral_bonus = 'referral_bonus'
    rpm_views = "rpm_views"
    survey_reward = 'survey_reward'  # For survey completion rewards
    survey_referral_bonus = 'survey_referral_bonus'  # For referral completing survey
    game_milestone_reward = 'game_milestone_reward'  # For 100-point milestone reward from spin game
    weekly_kpl_reward = 'weekly_kpl_reward'  # Weekly leaderboard payout
    donation_sent = 'donation_sent'  # For sending donations to creators
    donation_received = 'donation_received'  # For receiving donations from supporters
    wallet_funding = 'wallet_funding'
    weekly_top_contributor_reward = 'weekly_top_contributor_reward'


Account = models.TextChoices("Account", ["unverified", "pending", "verified", "declined","reviewing",'suspended'])
WithdrawType = models.TextChoices("Type", ['bank','wallet','transfer'])

Identity = models.TextChoices("Identity", ["NIGERIAN_NIN", "NIGERIAN_INTERNATIONAL_PASSPORT","NIGERIAN_PVC","NIGERIAN_DRIVERS_LICENSE"])