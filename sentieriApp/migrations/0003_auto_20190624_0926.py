# Generated by Django 2.2.1 on 2019-06-24 09:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sentieriApp', '0002_auto_20190624_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentiero',
            name='durata',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]