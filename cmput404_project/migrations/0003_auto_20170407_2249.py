# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-08 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmput404_project', '0002_auto_20170407_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='shared',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='host',
            field=models.URLField(default=b'http://127.0.0.1:8000'),
        ),
    ]