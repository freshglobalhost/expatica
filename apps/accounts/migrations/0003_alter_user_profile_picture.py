from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_bank_account_holder_user_bank_account_number_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="documents/profile_pictures",
                verbose_name="Profile picture",
            ),
        ),
    ]
