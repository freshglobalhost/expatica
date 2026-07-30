from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wallets", "0004_alter_wallet_currency_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet",
            name="bnb_balance",
            field=models.DecimalField(decimal_places=8, default=0, max_digits=18),
        ),
        migrations.AddField(
            model_name="wallet",
            name="ltc_balance",
            field=models.DecimalField(decimal_places=8, default=0, max_digits=18),
        ),
    ]
