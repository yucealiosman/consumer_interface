# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-07 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20161107_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='mybookings',
            name='book_time',
            field=models.TimeField(null=True),
        ),
    ]