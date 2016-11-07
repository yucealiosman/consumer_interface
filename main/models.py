# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import django.contrib.auth.models as auth_models


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    coral_code = models.CharField(max_length=100, unique=True)


class Destination(models.Model):
    name = models.CharField(max_length=100)
    coral_code = models.CharField(max_length=100, unique=True)


class MyTokens(models.Model):
    token_id = models.CharField(max_length=100, unique=True)
    used_flag = models.BooleanField(default=False)
    creation_time = models.CharField(max_length=100, null=True)


class MyBookings(models.Model):
    user = models.ForeignKey(auth_models.User, related_name='user')
    provision_code = models.CharField(max_length=255)
    hotel_code = models.CharField(max_length=50)
    hotel_name = models.CharField(max_length=50)
    coral_booking_code = models.CharField(max_length=255)
    room_type = models.CharField(max_length=50)
    room_description = models.CharField(max_length=255)
    pax_count = models.IntegerField()
    pax_names = models.TextField()
    price = models.FloatField()
    email = models.EmailField()
    book_time = models.CharField(null=True,max_length=50)