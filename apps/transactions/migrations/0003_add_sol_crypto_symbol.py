from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "transactions",
            "0002_transaction_crypto_amount_transaction_crypto_symbol_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="crypto_symbol",
            field=models.CharField(
                blank=True,
                choices=[
                    ("BTC", "Bitcoin"),
                    ("ETH", "Ethereum"),
                    ("USDT", "Tether"),
                    ("SOL", "Solana"),
                ],
                max_length=8,
                null=True,
            ),
        ),
    ]
