from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0005_alter_transaction_currency_code"),
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
                    ("BNB", "BNB"),
                    ("LTC", "Litecoin"),
                ],
                max_length=8,
                null=True,
            ),
        ),
    ]
