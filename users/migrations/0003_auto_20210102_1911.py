# Generated by Django 3.1.4 on 2021-01-02 11:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_auto_20210102_1636'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': '用户其他信息', 'verbose_name_plural': '用户其他信息'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='experience',
            field=models.IntegerField(default=0, verbose_name='经验值'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(max_length=20, verbose_name='学号'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户名'),
        ),
    ]
