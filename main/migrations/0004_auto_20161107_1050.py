# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-07 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20161107_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybookings',
            name='hotel_name',
            field=models.CharField(max_length=50),
        ),
    ]