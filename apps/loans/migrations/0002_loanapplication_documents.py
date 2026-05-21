from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("loans", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanapplication",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="annual_income",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="employer",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="employment_years",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="first_name",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="id_document",
            field=models.FileField(blank=True, upload_to="loan_applications/id/"),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="income_document",
            field=models.FileField(blank=True, upload_to="loan_applications/income/"),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="job_title",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="last_name",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="phone",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name="loanapplication",
            name="purpose",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
