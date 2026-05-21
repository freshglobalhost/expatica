import random

from django.db import migrations, models


def backfill_card_details(apps, schema_editor):
    VirtualCard = apps.get_model("cards", "VirtualCard")
    for card in VirtualCard.objects.select_related("user").all():
        updated = []
        user = card.user
        if not card.cardholder_name.strip():
            card.cardholder_name = (
                getattr(user, "full_name", None)
                or f"{user.first_name} {user.last_name}".strip()
                or user.email
            ).upper()[:128]
            updated.append("cardholder_name")
        if not card.card_number:
            digits = [4] + [random.randint(0, 9) for _ in range(14)] + [random.randint(0, 9)]
            card.card_number = "".join(str(d) for d in digits)
            card.last_four_digits = card.card_number[-4:]
            updated.append("card_number")
            updated.append("last_four_digits")
        if not card.cvv:
            card.cvv = f"{random.randint(100, 999)}"
            updated.append("cvv")
        if updated:
            card.save(update_fields=updated)


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualcard",
            name="cardholder_name",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="virtualcard",
            name="card_number",
            field=models.CharField(blank=True, db_index=True, max_length=19),
        ),
        migrations.AddField(
            model_name="virtualcard",
            name="cvv",
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.RunPython(backfill_card_details, migrations.RunPython.noop),
    ]
