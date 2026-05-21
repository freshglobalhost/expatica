from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wallets", "0002_alter_wallet_options_remove_wallet_is_primary_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet",
            name="sol_balance",
            field=models.DecimalField(decimal_places=8, default=0, max_digits=18),
        ),
    ]
