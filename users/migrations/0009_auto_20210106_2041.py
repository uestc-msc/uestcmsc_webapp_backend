# Generated by Django 3.1.4 on 2021-01-06 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20210106_2035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resetpasswordrequest',
            name='id',
        ),
        migrations.AlterField(
            model_name='resetpasswordrequest',
            name='token',
            field=models.CharField(max_length=32, primary_key=True, serialize=False),
        ),
    ]
