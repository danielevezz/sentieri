# Generated by Django 2.2.1 on 2019-06-26 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentieriApp', '0003_auto_20190626_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='esperienzapersonale',
            name='data_esperienza',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
